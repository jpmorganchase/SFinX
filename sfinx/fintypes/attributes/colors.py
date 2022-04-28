from colorsys import hls_to_rgb, rgb_to_hls

from openpyxl.styles.colors import COLOR_INDEX


class FinTabColors:
    """
    Handles mapping between different color models.
    Adapted from https://social.msdn.microsoft.com/Forums/en-US/e9d8c136-6d62-4098-9b1b-dac786149f43/excel-color-tint-algorithm-incorrect?forum=os_binaryfile#d3c2ac95-52e0-476b-86f1-e2a697f24969
    """

    RGBMAX = 0xFF  # Corresponds to 255
    HLSMAX = 240  # MS excel's tint function expects that HLS is base 240. see:
    BLACK = "00000000"

    @staticmethod
    def rgb_to_ms_hls(red, green=None, blue=None):
        """Converts rgb values in range (0,1) or a hex string of the form '[#aa]rrggbb'
        to HLSMAX based HLS, (alpha values are ignored)"""
        if green is None:
            if isinstance(red, str):
                if len(red) > 6:
                    red = red[-6:]  # Ignore preceding '#' and alpha values
                blue = int(red[4:], 16) / FinTabColors.RGBMAX
                green = int(red[2:4], 16) / FinTabColors.RGBMAX
                red = int(red[0:2], 16) / FinTabColors.RGBMAX
            else:
                red, green, blue = red
        h, l, s = rgb_to_hls(red, green, blue)
        return (
            int(round(h * FinTabColors.HLSMAX)),
            int(round(l * FinTabColors.HLSMAX)),
            int(round(s * FinTabColors.HLSMAX)),
        )

    @staticmethod
    def ms_hls_to_rgb(hue, lightness=None, saturation=None):
        """Converts HLSMAX based HLS values to rgb values in the range (0,1)"""
        if lightness is None:
            hue, lightness, saturation = hue
        return hls_to_rgb(
            hue / FinTabColors.HLSMAX,
            lightness / FinTabColors.HLSMAX,
            saturation / FinTabColors.HLSMAX,
        )

    @staticmethod
    def rgb_to_hex(red, green=None, blue=None):
        """Converts (0,1) based RGB values to a hex string 'rrggbb'"""
        if green is None:
            red, green, blue = red
        return (
            "%02x%02x%02x"
            % (
                int(round(red * FinTabColors.RGBMAX)),
                int(round(green * FinTabColors.RGBMAX)),
                int(round(blue * FinTabColors.RGBMAX)),
            )
        ).upper()

    @staticmethod
    def get_theme_colors(wb):
        """Gets theme colors from the workbook
        See: https://groups.google.com/forum/#!topic/openpyxl-users/I0k3TfqNLrc
        """
        from openpyxl.xml.functions import QName, fromstring

        xlmns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        root = fromstring(wb.loaded_theme)
        themeEl = root.find(QName(xlmns, "themeElements").text)
        colorSchemes = themeEl.findall(QName(xlmns, "clrScheme").text)
        firstColorScheme = colorSchemes[0]

        colors = []

        for c in [
            "lt1",
            "dk1",
            "lt2",
            "dk2",
            "accent1",
            "accent2",
            "accent3",
            "accent4",
            "accent5",
            "accent6",
        ]:
            accent = firstColorScheme.find(QName(xlmns, c).text)

            if "window" in accent.getchildren()[0].attrib["val"]:
                colors.append(accent.getchildren()[0].attrib["lastClr"])
            else:
                colors.append(accent.getchildren()[0].attrib["val"])

        return colors

    @staticmethod
    def tint_luminance(tint, lum):
        """Tints a HLSMAX based luminance
        See: http://ciintelligence.blogspot.co.uk/2012/02/converting-excel-theme-color-and-tint.html
        """
        if tint < 0:
            return int(round(lum * (1.0 + tint)))
        else:
            return int(round(lum * (1.0 - tint) + (FinTabColors.HLSMAX - FinTabColors.HLSMAX * (1.0 - tint))))

    @staticmethod
    def theme_and_tint_to_hex(wb, theme, tint):
        """Given a workbook, a theme number and a tint return a hex based rgb"""
        rgb = FinTabColors.get_theme_colors(wb)[theme]
        h, l, s = FinTabColors.rgb_to_ms_hls(rgb)
        return FinTabColors.rgb_to_hex(FinTabColors.ms_hls_to_rgb(h, FinTabColors.tint_luminance(tint, l), s))

    @staticmethod
    def index_to_hex(index):
        return COLOR_INDEX[index]

    @staticmethod
    def get_cell_fill_color_hex(cell):
        idx = cell.fill.start_color.index
        l = len(str(idx))
        if l == 8:
            return idx
        return FinTabColors.index_to_hex(idx)

    @staticmethod
    def get_cell_font_color_hex(cell):
        c = cell.font.color
        if not c:
            return FinTabColors.BLACK
        idx = cell.font.color.value
        l = len(str(idx))
        if l == 8:
            return idx
        return FinTabColors.index_to_hex(idx)
