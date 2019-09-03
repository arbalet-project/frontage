"""
    Arbalet - ARduino-BAsed LEd Table
    Operations on colors

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from numpy import isscalar, array
# From matplotlib.colors

cnames = {
    'aliceblue': array((0.9411764705882353, 0.9725490196078431, 1.0)),
    'antiquewhite': array((0.9803921568627451, 0.9215686274509803, 0.8431372549019608)),
    'aqua': array((0.0, 1.0, 1.0)),
    'aquamarine': array((0.4980392156862745, 1.0, 0.8313725490196079)),
    'azure': array((0.9411764705882353, 1.0, 1.0)),
    'beige': array((0.9607843137254902, 0.9607843137254902, 0.8627450980392157)),
    'bisque': array((1.0, 0.8941176470588236, 0.7686274509803922)),
    'bordeaux': array((0.82, 0.0, 0.22)),
    'black': array((0.0, 0.0, 0.0)),
    'blanchedalmond': array((1.0, 0.9215686274509803, 0.803921568627451)),
    'blue': array((0.0, 0.0, 1.0)),
    'blueviolet': array((0.5411764705882353, 0.16862745098039217, 0.8862745098039215)),
    'brown': array((0.6470588235294118, 0.16470588235294117, 0.16470588235294117)),
    'burlywood': array((0.8705882352941177, 0.7215686274509804, 0.5294117647058824)),
    'cadetblue': array((0.37254901960784315, 0.6196078431372549, 0.6274509803921569)),
    'chartreuse': array((0.4980392156862745, 1.0, 0.0)),
    'chocolate': array((0.8235294117647058, 0.4117647058823529, 0.11764705882352941)),
    'coral': array((1.0, 0.4980392156862745, 0.3137254901960784)),
    'cornflowerblue': array((0.39215686274509803, 0.5843137254901961, 0.9294117647058824)),
    'cornsilk': array((1.0, 0.9725490196078431, 0.8627450980392157)),
    'crimson': array((0.8627450980392157, 0.0784313725490196, 0.23529411764705882)),
    'cyan': array((0.0, 1.0, 1.0)),
    'darkblue': array((0.0, 0.0, 0.5450980392156862)),
    'darkcyan': array((0.0, 0.5450980392156862, 0.5450980392156862)),
    'darkgoldenrod': array((0.7215686274509804, 0.5254901960784314, 0.043137254901960784)),
    'darkgray': array((0.6627450980392157, 0.6627450980392157, 0.6627450980392157)),
    'darkgreen': array((0.0, 0.39215686274509803, 0.0)),
    'darkgrey': array((0.6627450980392157, 0.6627450980392157, 0.6627450980392157)),
    'darkkhaki': array((0.7411764705882353, 0.7176470588235294, 0.4196078431372549)),
    'darkmagenta': array((0.5450980392156862, 0.0, 0.5450980392156862)),
    'darkolivegreen': array((0.3333333333333333, 0.4196078431372549, 0.1843137254901961)),
    'darkorange': array((1.0, 0.5490196078431373, 0.0)),
    'darkorchid': array((0.6, 0.19607843137254902, 0.8)),
    'darkred': array((0.5450980392156862, 0.0, 0.0)),
    'darksage': array((0.34901960784313724, 0.5215686274509804, 0.33725490196078434)),
    'darksalmon': array((0.9137254901960784, 0.5882352941176471, 0.47843137254901963)),
    'darkseagreen': array((0.5607843137254902, 0.7372549019607844, 0.5607843137254902)),
    'darkslateblue': array((0.2823529411764706, 0.23921568627450981, 0.5450980392156862)),
    'darkslategray': array((0.1843137254901961, 0.30980392156862746, 0.30980392156862746)),
    'darkslategrey': array((0.1843137254901961, 0.30980392156862746, 0.30980392156862746)),
    'darkturquoise': array((0.0, 0.807843137254902, 0.8196078431372549)),
    'darkviolet': array((0.5803921568627451, 0.0, 0.8274509803921568)),
    'deeppink': array((1.0, 0.0784313725490196, 0.5764705882352941)),
    'deepskyblue': array((0.0, 0.7490196078431373, 1.0)),
    'dimgray': array((0.4117647058823529, 0.4117647058823529, 0.4117647058823529)),
    'dimgrey': array((0.4117647058823529, 0.4117647058823529, 0.4117647058823529)),
    'dodgerblue': array((0.11764705882352941, 0.5647058823529412, 1.0)),
    'firebrick': array((0.6980392156862745, 0.13333333333333333, 0.13333333333333333)),
    'floralwhite': array((1.0, 0.9803921568627451, 0.9411764705882353)),
    'forestgreen': array((0.13333333333333333, 0.5450980392156862, 0.13333333333333333)),
    'fuchsia': array((1.0, 0.0, 1.0)),
    'gainsboro': array((0.8627450980392157, 0.8627450980392157, 0.8627450980392157)),
    'ghostwhite': array((0.9725490196078431, 0.9725490196078431, 1.0)),
    'gold': array((1.0, 0.8431372549019608, 0.0)),
    'goldenrod': array((0.8549019607843137, 0.6470588235294118, 0.12549019607843137)),
    'gray': array((0.5019607843137255, 0.5019607843137255, 0.5019607843137255)),
    'green': array((0.0, 0.5019607843137255, 0.0)),
    'greenyellow': array((0.6784313725490196, 1.0, 0.1843137254901961)),
    'grey': array((0.5019607843137255, 0.5019607843137255, 0.5019607843137255)),
    'honeydew': array((0.9411764705882353, 1.0, 0.9411764705882353)),
    'hotpink': array((1.0, 0.4117647058823529, 0.7058823529411765)),
    'indianred': array((0.803921568627451, 0.3607843137254902, 0.3607843137254902)),
    'indigo': array((0.29411764705882354, 0.0, 0.5098039215686274)),
    'ivory': array((1.0, 1.0, 0.9411764705882353)),
    'khaki': array((0.9411764705882353, 0.9019607843137255, 0.5490196078431373)),
    'lavender': array((0.9019607843137255, 0.9019607843137255, 0.9803921568627451)),
    'lavenderblush': array((1.0, 0.9411764705882353, 0.9607843137254902)),
    'lawngreen': array((0.48627450980392156, 0.9882352941176471, 0.0)),
    'lemonchiffon': array((1.0, 0.9803921568627451, 0.803921568627451)),
    'lightblue': array((0.6784313725490196, 0.8470588235294118, 0.9019607843137255)),
    'lightcoral': array((0.9411764705882353, 0.5019607843137255, 0.5019607843137255)),
    'lightcyan': array((0.8784313725490196, 1.0, 1.0)),
    'lightgoldenrodyellow': array((0.9803921568627451, 0.9803921568627451, 0.8235294117647058)),
    'lightgray': array((0.8274509803921568, 0.8274509803921568, 0.8274509803921568)),
    'lightgreen': array((0.5647058823529412, 0.9333333333333333, 0.5647058823529412)),
    'lightgrey': array((0.8274509803921568, 0.8274509803921568, 0.8274509803921568)),
    'lightpink': array((1.0, 0.7137254901960784, 0.7568627450980392)),
    'lightsage': array((0.7372549019607844, 0.9254901960784314, 0.6745098039215687)),
    'lightsalmon': array((1.0, 0.6274509803921569, 0.47843137254901963)),
    'lightseagreen': array((0.12549019607843137, 0.6980392156862745, 0.6666666666666666)),
    'lightskyblue': array((0.5294117647058824, 0.807843137254902, 0.9803921568627451)),
    'lightslategray': array((0.4666666666666667, 0.5333333333333333, 0.6)),
    'lightslategrey': array((0.4666666666666667, 0.5333333333333333, 0.6)),
    'lightsteelblue': array((0.6901960784313725, 0.7686274509803922, 0.8705882352941177)),
    'lightyellow': array((1.0, 1.0, 0.8784313725490196)),
    'lime': array((0.0, 1.0, 0.0)),
    'limegreen': array((0.19607843137254902, 0.803921568627451, 0.19607843137254902)),
    'linen': array((0.9803921568627451, 0.9411764705882353, 0.9019607843137255)),
    'magenta': array((1.0, 0.0, 1.0)),
    'maroon': array((0.5019607843137255, 0.0, 0.0)),
    'mediumaquamarine': array((0.4, 0.803921568627451, 0.6666666666666666)),
    'mediumblue': array((0.0, 0.0, 0.803921568627451)),
    'mediumorchid': array((0.7294117647058823, 0.3333333333333333, 0.8274509803921568)),
    'mediumpurple': array((0.5764705882352941, 0.4392156862745098, 0.8588235294117647)),
    'mediumseagreen': array((0.23529411764705882, 0.7019607843137254, 0.44313725490196076)),
    'mediumslateblue': array((0.4823529411764706, 0.40784313725490196, 0.9333333333333333)),
    'mediumspringgreen': array((0.0, 0.9803921568627451, 0.6039215686274509)),
    'mediumturquoise': array((0.2823529411764706, 0.8196078431372549, 0.8)),
    'mediumvioletred': array((0.7803921568627451, 0.08235294117647059, 0.5215686274509804)),
    'midnightblue': array((0.09803921568627451, 0.09803921568627451, 0.4392156862745098)),
    'mintcream': array((0.9607843137254902, 1.0, 0.9803921568627451)),
    'mistyrose': array((1.0, 0.8941176470588236, 0.8823529411764706)),
    'moccasin': array((1.0, 0.8941176470588236, 0.7098039215686275)),
    'navajowhite': array((1.0, 0.8705882352941177, 0.6784313725490196)),
    'navy': array((0.0, 0.0, 0.5019607843137255)),
    'oldlace': array((0.9921568627450981, 0.9607843137254902, 0.9019607843137255)),
    'olive': array((0.5019607843137255, 0.5019607843137255, 0.0)),
    'olivedrab': array((0.4196078431372549, 0.5568627450980392, 0.13725490196078433)),
    'orange': array((1.0, 0.6470588235294118, 0.0)),
    'orangered': array((1.0, 0.27058823529411763, 0.0)),
    'orchid': array((0.8549019607843137, 0.4392156862745098, 0.8392156862745098)),
    'palegoldenrod': array((0.9333333333333333, 0.9098039215686274, 0.6666666666666666)),
    'palegreen': array((0.596078431372549, 0.984313725490196, 0.596078431372549)),
    'paleturquoise': array((0.6862745098039216, 0.9333333333333333, 0.9333333333333333)),
    'palevioletred': array((0.8588235294117647, 0.4392156862745098, 0.5764705882352941)),
    'papayawhip': array((1.0, 0.9372549019607843, 0.8352941176470589)),
    'peachpuff': array((1.0, 0.8549019607843137, 0.7254901960784313)),
    'peru': array((0.803921568627451, 0.5215686274509804, 0.24705882352941178)),
    'pink': array((1.0, 0.7529411764705882, 0.796078431372549)),
    'plum': array((0.8666666666666667, 0.6274509803921569, 0.8666666666666667)),
    'powderblue': array((0.6901960784313725, 0.8784313725490196, 0.9019607843137255)),
    'purple': array((0.5019607843137255, 0.0, 0.5019607843137255)),
    'red': array((1.0, 0.0, 0.0)),
    'rosybrown': array((0.7372549019607844, 0.5607843137254902, 0.5607843137254902)),
    'royalblue': array((0.2549019607843137, 0.4117647058823529, 0.8823529411764706)),
    'saddlebrown': array((0.5450980392156862, 0.27058823529411763, 0.07450980392156863)),
    'sage': array((0.5294117647058824, 0.6823529411764706, 0.45098039215686275)),
    'salmon': array((0.9803921568627451, 0.5019607843137255, 0.4470588235294118)),
    'sandybrown': array((0.9803921568627451, 0.6431372549019608, 0.3764705882352941)),
    'seagreen': array((0.1803921568627451, 0.5450980392156862, 0.3411764705882353)),
    'seashell': array((1.0, 0.9607843137254902, 0.9333333333333333)),
    'sienna': array((0.6274509803921569, 0.3215686274509804, 0.17647058823529413)),
    'silver': array((0.7529411764705882, 0.7529411764705882, 0.7529411764705882)),
    'skyblue': array((0.5294117647058824, 0.807843137254902, 0.9215686274509803)),
    'slateblue': array((0.41568627450980394, 0.35294117647058826, 0.803921568627451)),
    'slategray': array((0.4392156862745098, 0.5019607843137255, 0.5647058823529412)),
    'slategrey': array((0.4392156862745098, 0.5019607843137255, 0.5647058823529412)),
    'snow': array((1.0, 0.9803921568627451, 0.9803921568627451)),
    'springgreen': array((0.0, 1.0, 0.4980392156862745)),
    'steelblue': array((0.27450980392156865, 0.5098039215686274, 0.7058823529411765)),
    'tan': array((0.8235294117647058, 0.7058823529411765, 0.5490196078431373)),
    'teal': array((0.0, 0.5019607843137255, 0.5019607843137255)),
    'thistle': array((0.8470588235294118, 0.7490196078431373, 0.8470588235294118)),
    'tomato': array((1.0, 0.38823529411764707, 0.2784313725490196)),
    'turquoise': array((0.25098039215686274, 0.8784313725490196, 0.8156862745098039)),
    'violet': array((0.9333333333333333, 0.5098039215686274, 0.9333333333333333)),
    'wheat': array((0.9607843137254902, 0.8705882352941177, 0.7019607843137254)),
    'white': array((1.0, 1.0, 1.0)),
    'whitesmoke': array((0.9607843137254902, 0.9607843137254902, 0.9607843137254902)),
    'yellow': array((1.0, 1.0, 0.0)),
    'yellowgreen': array((0.6039215686274509, 0.803921568627451, 0.19607843137254902))
}


def name_to_rgb(color_name):
    global cnames
    return cnames[color_name]


def name_to_hsv(color_name):
    return rgb_to_hsv(name_to_rgb(color_name))

def rgb255_to_rgb(red255, green255, blue255):
    red = color255_to_color(red255)
    green = color255_to_color(green255)
    blue = color255_to_color(blue255)
    return red, green, blue

def color255_to_color(color255):
    # This might raise exceptions          
    return float(color255)/float(255)

# HSV: Hue, Saturation, Value
# H: position in the spectrum
# S: color saturation ("purity")
# V: color brightness

def rgb_to_hsv(r, g=None, b=None):
    if g is None and b is None:
        r, g, b = r
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return 0.0, 0.0, v
    s = (maxc - minc) / maxc
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)
    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc
    h = (h / 6.0) % 1.0
    return h, s, v


def hsv_to_rgb(h, s=None, v=None):
    if s is None and v is None:
        h, s, v = h
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)  # XXX assume int() truncates!
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    # Cannot get here


def __to_array(pixel):
    if isinstance(pixel, str):
        pixel = name_to_rgb(pixel)
    return array(pixel)


def add(pixel_1, pixel_2):
    """
    Addition of two RGB or named pixels
    :param pixel_: Color name or tuple, list, array
    :param pixel_2: Color name or tuple, list, array
    :return: array(r, g, b)
    """
    pixel_1 = __to_array(pixel_1)
    pixel_2 = __to_array(pixel_2)

    return pixel_1 + pixel_2


def mul(pixel, scalar):
    """
    Multiplication of a RGB or named pixel with a scalar
    :param pixel: Color name or tuple, list, array
    :param scalar: int or float to multiply the array with
    :return: array(r, g, b)
    """
    pixel = __to_array(pixel)

    if not isscalar(scalar):
        raise TypeError(
            "Expected a scalar for pixel multiplication, got {}".format(
                type(scalar)))
    return pixel * scalar


def equal(pixel_1, pixel_2):
    """
    Return true if these two colors are strictly equal
    :param pixel_1: Color name or tuple, list, array
    :param pixel_2: Color name or tuple, list, array
    :return: True if they are strictly equal, False otherwise
    """
    pixel_1 = __to_array(pixel_1)
    pixel_2 = __to_array(pixel_2)

    return (pixel_1 == pixel_2).all(0)
