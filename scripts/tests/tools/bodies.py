import pygame
import math

# Constants
GRAVITY = 100
FRICTION = 0.98
ELASTICITY = 0.1  # Coefficient of restitution for bouncy collisions

class Rigidbody():
    def __init__(self, x, y, width, height, mass=1):
        self.mass = mass
        self.inv_mass = 1 / mass if mass > 0 else 0
        self.rect = pygame.Rect(x, y, width, height)
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.angular_velocity = 0
        self.rotation = 0
        self.is_grounded = False

    def apply_force(self, force):
        self.acceleration += force * self.inv_mass

    def apply_torque(self, torque):
        inertia = (1 / 12) * self.mass * (self.rect.width ** 2 + self.rect.height ** 2)
        self.angular_velocity += torque / inertia

    def apply_gravity(self):
        if not self.is_grounded:
            self.apply_force(pygame.Vector2(0, GRAVITY * self.mass))

    def update(self, dt):
        # Update velocity and position
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.rotation += self.angular_velocity * dt
        self.rect.center = self.position

        # Apply friction
        if self.is_grounded:
            self.velocity.x *= FRICTION

        # Reset acceleration
        self.acceleration = pygame.Vector2(0, 0)

    def check_collision(self, other):
        if isinstance(other, Circle):
            self.aabb_circle_collision(other)
        elif isinstance(self, Circle) and isinstance(other, Circle):
            self.circle_collision(other)
        else:
            self.aabb_collision(other)

    def aabb_collision(self, other):
        if self.rect.colliderect(other.rect):
            penetration_vector = self.resolve_penetration(self.rect, other.rect)
            self.position -= penetration_vector / 2
            other.position += penetration_vector / 2
            normal = pygame.Vector2(0, -1 if penetration_vector.y else 1)
            self.resolve_velocity(other, normal)

    def aabb_circle_collision(self, circle):
        closest_x = max(self.rect.left, min(circle.position.x, self.rect.right))
        closest_y = max(self.rect.top, min(circle.position.y, self.rect.bottom))
        closest_point = pygame.Vector2(closest_x, closest_y)
        distance_vector = circle.position - closest_point
        distance = distance_vector.length()
        if distance < circle.radius:
            overlap = circle.radius - distance
            normal = distance_vector.normalize()
            circle.position += normal * overlap
            self.resolve_velocity(circle, normal)

    def resolve_penetration(self, rect1, rect2):
        dx = min(rect1.right - rect2.left, rect2.right - rect1.left)
        dy = min(rect1.bottom - rect2.top, rect2.bottom - rect1.top)
        if abs(dx) < abs(dy):
            return pygame.Vector2(dx, 0)
        else:
            return pygame.Vector2(0, dy)

    def resolve_velocity(self, other, normal):
        relative_velocity = self.velocity - other.velocity
        normal_velocity = relative_velocity.dot(normal)
        if normal_velocity > 0:
            return

        impulse = -(1 + ELASTICITY) * normal_velocity
        impulse /= self.inv_mass + other.inv_mass

        impulse_vector = impulse * normal
        self.velocity += impulse_vector * self.inv_mass
        other.velocity -= impulse_vector * other.inv_mass

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

class Circle(Rigidbody):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, mass)
        self.radius = radius

    def circle_collision(self, other):
        distance_vector = self.position - other.position
        distance = distance_vector.length()
        if distance < self.radius + other.radius:
            overlap = (self.radius + other.radius) - distance
            normal = distance_vector.normalize()
            self.position += normal * (overlap / 2)
            other.position -= normal * (overlap / 2)
            self.resolve_velocity(other, normal)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.position.x), int(self.position.y)), self.radius)

class Platform(Rigidbody):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, mass=math.inf)  # Infinite mass to make it static

    def apply_gravity(self):
        pass  # Platforms do not experience gravity

    def update(self, dt):
        pass  # Platforms do not update their position

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 255), self.rect)  # Draw platform in blue

class CharacterBody2D():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.position = pygame.Vector2(self.rect.topleft)
        self.velocity = pygame.Vector2(0, 0)
        self.is_grounded = False
        self.normal = pygame.Vector2(0, 0)

    def move_and_slide(self, velocity, floor_normal=pygame.Vector2(0, -1)):
        self.velocity = velocity

        # Apply movement
        self.position += self.velocity
        self.rect.topleft = self.position

        # Reset normal and grounded state
        self.normal = pygame.Vector2(0, 0)
        self.is_grounded = False

        # Simulate collisions
        for other in objects:
            if other is not self and self.rect.colliderect(other.rect):
                if isinstance(other, Rigidbody) and other.mass < math.inf:
                    self.push_rigidbody(other)  # Apply force to the rigidbody
                self.resolve_collision(other)

    def push_rigidbody(self, rigidbody):
        """ Apply force to move a Rigidbody when pushing it. """
        push_direction = pygame.Vector2(0, 0)

        # Check if pushing from the sides
        if self.velocity.x > 0 and self.rect.right > rigidbody.rect.left:  # Pushing right
            push_direction = pygame.Vector2(1, 0)
        elif self.velocity.x < 0 and self.rect.left < rigidbody.rect.right:  # Pushing left
            push_direction = pygame.Vector2(-1, 0)

        force_magnitude = 100  # Adjust this value for stronger pushing force
        rigidbody.apply_force(push_direction * force_magnitude)

    def resolve_collision(self, other):
        penetration_vector = self.resolve_penetration(self.rect, other.rect)
        
        # Correctly set the collision normal based on the penetration direction
        if abs(penetration_vector.x) > abs(penetration_vector.y):
            # Horizontal collision
            normal = pygame.Vector2(1 if penetration_vector.x > 0 else -1, 0)
        else:
            # Vertical collision
            normal = pygame.Vector2(0, 1 if penetration_vector.y > 0 else -1)

        # Apply the penetration resolution
        self.position -= penetration_vector
        self.rect.topleft = self.position

        # Update normal and grounded state
        if normal.y < 0:  # Collision from the bottom
            self.is_grounded = True
        self.normal = normal            

    def resolve_penetration(self, rect1, rect2):
        dx = min(rect1.right - rect2.left, rect2.right - rect1.left)
        dy = min(rect1.bottom - rect2.top, rect2.bottom - rect1.top)

        if abs(dx) < abs(dy):  # Horizontal collision
            return pygame.Vector2(-dx if rect1.centerx > rect2.centerx else dx, 0)
        else:  # Vertical collision
            return pygame.Vector2(0, -dy if rect1.centery > rect2.centery else dy)


    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create objects
ball1 = Circle(420, 150, 20, mass=2)
ball2 = Circle(400, 100, 20, mass=3)
box1 = Rigidbody(300, 300, 50, 50, mass=5)

floor = Platform(0, 550, 800, 50)
character = CharacterBody2D(100, 500, 40, 40)

objects = [ball1, ball2, box1, floor]

running = True
while running:
    dt = clock.tick(60) / 1000  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Character movement
    keys = pygame.key.get_pressed()
    move_velocity = pygame.Vector2(0, 0)
    if keys[pygame.K_LEFT]:
        move_velocity.x = -200 * dt
    if keys[pygame.K_RIGHT]:
        move_velocity.x = 200 * dt
    if keys[pygame.K_UP]:
        move_velocity.y = -300 * dt
    if keys[pygame.K_DOWN]:
        move_velocity.y = 300 * dt
    # Apply gravity to character
    move_velocity.y += GRAVITY*0.01

    # Move and slide character
    character.move_and_slide(move_velocity)

    # Physics update for other objects
    for obj in objects:
        obj.apply_gravity()
        obj.update(dt)

    for i, obj1 in enumerate(objects):
        for obj2 in objects[i + 1:]:
            obj1.check_collision(obj2)

    # Drawing
    screen.fill((0, 0, 0))
    for obj in objects:
        obj.draw(screen)
    character.draw(screen)

    pygame.display.flip()

pygame.quit()
