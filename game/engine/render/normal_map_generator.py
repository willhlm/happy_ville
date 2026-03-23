import math

import numpy as np
import pygame


class NormalMapGenerator:
    def __init__(
        self,
        game_objects,
        detail_depth=250,
        edge_depth=100,
        bevel_distance=60,
        detail_blur_radius=6,
        bevel_blur_radius=10,
        use_soft_bevel=True,
        smooth_strength=0.0,
        smooth_passes=0,
    ):
        self.game_objects = game_objects
        self.display = game_objects.game.display
        self.shader = game_objects.shaders.get("normal_map_generator")
        self.detail_depth = detail_depth
        self.edge_depth = edge_depth
        self.bevel_distance = bevel_distance
        self.detail_blur_radius = detail_blur_radius
        self.bevel_blur_radius = bevel_blur_radius
        self.use_soft_bevel = use_soft_bevel
        self.smooth_strength = smooth_strength
        self.smooth_passes = smooth_passes

    def generate_texture(self, surface):
        generated_surface = self.generate_surface(surface)
        return self.display.surface_to_texture(generated_surface)

    def generate_surface(self, surface):
        normal_surface = self._generate_base_surface(surface)
        if self.shader and self.smooth_passes > 0 and self.smooth_strength > 0:
            return self._smooth_surface(normal_surface)
        return normal_surface

    def _generate_base_surface(self, surface):
        width, height = surface.get_size()
        rgb = pygame.surfarray.array3d(surface).astype(np.float32).transpose(1, 0, 2)
        alpha_u8 = pygame.surfarray.array_alpha(surface).astype(np.uint8).T
        alpha = alpha_u8.astype(np.float32) / 255.0
        alpha_mask = alpha > 0.0

        luma = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
        detail_height = luma * 10.0

        detail_height = self._blur_height_map(detail_height, self.detail_blur_radius)
        bevel_height = self._build_alpha_bevel_height(alpha_mask)
        bevel_height = self._blur_height_map(bevel_height, self.bevel_blur_radius)

        detail_nx, detail_ny, detail_nz = self._normal_from_height(detail_height, alpha_mask, self.detail_depth)
        bevel_nx, bevel_ny, bevel_nz = self._normal_from_height(
            bevel_height,
            alpha_mask,
            self.edge_depth * self.bevel_distance,
        )

        nx = detail_nx * 1.5 + bevel_nx * 1.5
        ny = detail_ny * 1.5 + bevel_ny * 1.5
        nz = detail_nz * 1.5 + bevel_nz * 1.5

        length = np.sqrt(nx * nx + ny * ny + nz * nz)
        length[length == 0.0] = 1.0
        nx /= length
        ny /= length
        nz /= length

        out = np.zeros((height, width, 4), dtype=np.uint8)
        out[:, :, 0] = np.clip((nx * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
        out[:, :, 1] = np.clip((ny * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
        out[:, :, 2] = np.clip((nz * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
        out[:, :, 3] = alpha_u8
        out[~alpha_mask] = 0

        return pygame.image.frombuffer(out.tobytes(), (width, height), "RGBA").convert_alpha()

    def _blur_height_map(self, height_map, radius):
        if radius <= 0:
            return height_map

        sigma = max(radius / 3.0, 1e-4)
        kernel = self._gaussian_kernel(radius, sigma)
        horizontal = np.zeros_like(height_map, dtype=np.float32)
        horizontal_weights = np.zeros_like(height_map, dtype=np.float32)

        for offset, weight in kernel:
            shifted = self._shift_with_zero(height_map, axis=1, offset=offset)
            weights = self._shift_with_zero(np.ones_like(height_map, dtype=np.float32), axis=1, offset=offset)
            horizontal += shifted * weight
            horizontal_weights += weights * weight

        horizontal = np.divide(horizontal, horizontal_weights, out=np.zeros_like(horizontal), where=horizontal_weights > 0.0)

        blurred = np.zeros_like(height_map, dtype=np.float32)
        blurred_weights = np.zeros_like(height_map, dtype=np.float32)
        for offset, weight in kernel:
            shifted = self._shift_with_zero(horizontal, axis=0, offset=offset)
            weights = self._shift_with_zero(np.ones_like(horizontal, dtype=np.float32), axis=0, offset=offset)
            blurred += shifted * weight
            blurred_weights += weights * weight

        return np.divide(blurred, blurred_weights, out=np.zeros_like(blurred), where=blurred_weights > 0.0)

    def _build_alpha_bevel_height(self, alpha_mask):
        if self.bevel_distance <= 0:
            return np.zeros(alpha_mask.shape, dtype=np.float32)

        if np.all(alpha_mask):
            return np.ones(alpha_mask.shape, dtype=np.float32)

        dist = np.sqrt(self._edt_2d((~alpha_mask).astype(np.float32)))
        dist = np.minimum(dist, float(self.bevel_distance))
        value = np.clip((dist * 255.0) / float(self.bevel_distance), 0.0, 255.0)
        if self.use_soft_bevel:
            unit = value / 255.0
            value = np.sqrt(np.maximum(0.0, 1.0 - (unit - 1.0) ** 2)) * 255.0
        return (value / 255.0).astype(np.float32)

    def _gaussian_kernel(self, radius, sigma):
        kernel = []
        for offset in range(-radius, radius + 1):
            weight = math.exp(-(offset * offset) / (2.0 * sigma * sigma))
            kernel.append((offset, weight))
        return kernel

    def _normal_from_height(self, height_map, alpha_mask, depth):
        height, width = height_map.shape
        dx = np.empty_like(height_map, dtype=np.float32)
        dy = np.empty_like(height_map, dtype=np.float32)

        if width >= 3:
            dx[:, 0] = -3.0 * height_map[:, 0] + 4.0 * height_map[:, 1] - height_map[:, 2]
            dx[:, -1] = 3.0 * height_map[:, -1] - 4.0 * height_map[:, -2] + height_map[:, -3]
            dx[:, 1:-1] = -height_map[:, :-2] + height_map[:, 2:]
        elif width == 2:
            dx[:, 0] = height_map[:, 1] - height_map[:, 0]
            dx[:, 1] = height_map[:, 1] - height_map[:, 0]
        else:
            dx[:, 0] = 0.0

        if height >= 3:
            dy[0, :] = -3.0 * height_map[0, :] + 4.0 * height_map[1, :] - height_map[2, :]
            dy[-1, :] = 3.0 * height_map[-1, :] - 4.0 * height_map[-2, :] + height_map[-3, :]
            dy[1:-1, :] = -height_map[:-2, :] + height_map[2:, :]
        elif height == 2:
            dy[0, :] = height_map[1, :] - height_map[0, :]
            dy[1, :] = height_map[1, :] - height_map[0, :]
        else:
            dy[0, :] = 0.0

        nx = -dx * (depth / 100.0)
        ny = dy * (depth / 100.0)
        nz = np.ones_like(height_map, dtype=np.float32)

        nx = np.where(alpha_mask, nx, 0.0)
        ny = np.where(alpha_mask, ny, 0.0)
        nz = np.where(alpha_mask, nz, 1.0)
        return nx, ny, nz

    def _shift_with_zero(self, array, axis, offset):
        shifted = np.roll(array, offset, axis=axis)
        if offset > 0:
            index = [slice(None)] * array.ndim
            index[axis] = slice(0, offset)
            shifted[tuple(index)] = 0.0
        elif offset < 0:
            index = [slice(None)] * array.ndim
            index[axis] = slice(offset, None)
            shifted[tuple(index)] = 0.0
        return shifted

    def _edt_1d(self, values):
        n = values.shape[0]
        v = np.zeros(n, dtype=np.int32)
        z = np.zeros(n + 1, dtype=np.float32)
        d = np.zeros(n, dtype=np.float32)
        k = 0
        v[0] = 0
        z[0] = -np.inf
        z[1] = np.inf

        for q in range(1, n):
            s = ((values[q] + q * q) - (values[v[k]] + v[k] * v[k])) / (2.0 * (q - v[k]))
            while s <= z[k]:
                k -= 1
                s = ((values[q] + q * q) - (values[v[k]] + v[k] * v[k])) / (2.0 * (q - v[k]))
            k += 1
            v[k] = q
            z[k] = s
            z[k + 1] = np.inf

        k = 0
        for q in range(n):
            while z[k + 1] < q:
                k += 1
            diff = q - v[k]
            d[q] = diff * diff + values[v[k]]
        return d

    def _edt_2d(self, binary_background):
        inf = np.float32(1e10)
        f = np.where(binary_background > 0.0, 0.0, inf).astype(np.float32)
        height, width = f.shape

        g = np.empty_like(f)
        for x in range(width):
            g[:, x] = self._edt_1d(f[:, x])

        d = np.empty_like(g)
        for y in range(height):
            d[y, :] = self._edt_1d(g[y, :])
        return d

    def _normalize(self, nx, ny, nz):
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length == 0:
            return 0.0, 0.0, 1.0
        return nx / length, ny / length, nz / length

    def _smooth_surface(self, surface):
        source_texture = self.display.surface_to_texture(surface)
        ping = self.display.make_layer(surface.get_size())
        pong = self.display.make_layer(surface.get_size())

        try:
            input_texture = source_texture
            output_layer = ping
            for _ in range(self.smooth_passes):
                output_layer.clear(128, 128, 255, 0)
                self.shader["texel_size"] = (1.0 / surface.get_width(), 1.0 / surface.get_height())
                self.shader["smooth_strength"] = self.smooth_strength
                self.display.render(input_texture, output_layer, shader=self.shader)
                input_texture = output_layer.texture
                output_layer = pong if output_layer is ping else ping

            return self._texture_to_surface(input_texture)
        finally:
            source_texture.release()
            ping.release()
            pong.release()

    def _texture_to_surface(self, texture):
        raw = texture.read(alignment=1)
        surface = pygame.image.fromstring(raw, texture.size, "RGBA").convert_alpha()
        return pygame.transform.flip(surface, False, True)
