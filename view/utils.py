import pygame.draw
from pygame.gfxdraw import aacircle, filled_circle


def draw_rounded_rect(surface, color, rect, border_radius):
    """Draw a rectangle with rounded corners.

    Would prefer this:
        ``pygame.draw.rect(surface, color, rect, border_radius=corner_radius)``
    but this option is not yet supported in pygame < 2.0.0 so do it ourselves.

    We use anti-aliased circles to make the corners smoother
    """

    if rect.width < 2 * border_radius or rect.height < 2 * border_radius:
        raise ValueError(f"Both height (rect.height) and width (rect.width) must be > 2 * corner radius ({border_radius})")

    # Need to use anti aliasing circle drawing routines to smooth the corners
    aacircle(surface, rect.left + border_radius, rect.top + border_radius, border_radius, color)
    aacircle(surface, rect.right - border_radius - 1, rect.top + border_radius, border_radius, color)
    aacircle(surface, rect.left + border_radius, rect.bottom - border_radius - 1, border_radius, color)
    aacircle(surface, rect.right - border_radius - 1, rect.bottom - border_radius - 1, border_radius, color)

    filled_circle(surface, rect.left + border_radius, rect.top + border_radius, border_radius, color)
    filled_circle(surface, rect.right - border_radius - 1, rect.top + border_radius, border_radius, color)
    filled_circle(surface, rect.left + border_radius, rect.bottom - border_radius - 1, border_radius, color)
    filled_circle(surface, rect.right - border_radius - 1, rect.bottom - border_radius - 1, border_radius, color)

    rect_tmp = pygame.Rect(rect)

    rect_tmp.width -= 2 * border_radius
    rect_tmp.center = rect.center
    pygame.draw.rect(surface, color, rect_tmp)

    rect_tmp.width = rect.width
    rect_tmp.height -= 2 * border_radius
    rect_tmp.center = rect.center
    pygame.draw.rect(surface, color, rect_tmp)


def draw_bordered_rounded_rect(surface, color, rect, border_color, border_radius, border_thickness):
    if border_radius < 0:
        raise ValueError(f"Border radius ({border_radius}) must be >= 0")

    rect_tmp = pygame.Rect(rect)

    if border_thickness:
        if border_radius <= 0:
            pygame.draw.rect(surface, border_color, rect_tmp)
        else:
            draw_rounded_rect(surface, border_color, rect_tmp, border_radius)

        rect_tmp.inflate_ip(-2 * border_thickness, -2 * border_thickness)
        inner_radius = border_radius - border_thickness + 1
    else:
        inner_radius = border_radius

    if inner_radius <= 0:
        pygame.draw.rect(surface, color, rect_tmp)
    else:
        draw_rounded_rect(surface, color, rect_tmp, inner_radius)


def draw_text(surface, text, color, rect, font, antialias=False, background=None):
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2

    # Get the height of the font
    font_height = font.size("Tg")[1]

    for text in text.split('\n'):
        while text:
            i = 1

            # Determine if the row of text will be outside our area
            if y + font_height > rect.bottom:
                break

            # Determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            # If we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1 if not nl else text.rfind("\n", 0, i) + 1

            # Render the line and blit it to the surface
            if background:
                image = font.render(text[:i], 1, color, background)
                image.set_colorkey(background)
            else:
                image = font.render(text[:i], antialias, color)

            surface.blit(image, (rect.left, y))
            y += font_height + line_spacing

            # Remove the text we just blitted
            text = text[i:]

    return text
