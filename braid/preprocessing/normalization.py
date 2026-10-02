import re

def clean_text(value):

    if value is None:
        return None

    value = str(value)

    value = value.replace(
        "\u200e",
        ""
    )

    value = value.replace(
        "\ufeff",
        ""
    )

    value = value.strip()

    if value == "":
        return None

    return value


def normalize_bluetooth(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.replace(
        "Bluetooth Specification Version ",
        ""
    )

    value = value.replace(
        "Bluetooth ",
        ""
    )

    value = value.replace(
        "Version ",
        ""
    )

    value = value.replace(
        "BT",
        ""
    )

    value = value.strip()

    if value in {
        "Class 1 Bluetooth",
        "Class 1"
    }:
        return None

    if "Wi-Fi" in value:
        return None

    return value


def normalize_operating_system(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    replacements = {

        "Windows 11 Home in S Mode":
            "Windows 11 Home",

        "Windows 11 Home, Copilot+ PC":
            "Windows 11 Home",

        "Windows 11":
            "Windows 11 Home"
    }

    return replacements.get(
        value,
        value
    )


def normalize_wifi(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.lower()

    if (
        "802.11be" in value
        or "802.11.be" in value
        or "wi-fi 7" in value
        or "wifi 7" in value
    ):
        return "Wi-Fi 7"

    if (
        "802.11ax" in value
        or "wi-fi 6e" in value
        or "wifi 6e" in value
    ):
        return "Wi-Fi 6E"

    if (
        "wi-fi 6" in value
        or "wifi 6" in value
        or "wi-fi6" in value
        or "wifi6" in value
    ):
        return "Wi-Fi 6"

    if "802.11ac" in value:
        return "Wi-Fi 5"

    if (
        "wi-fi" in value
        or "wifi" in value
    ):
        return "Wi-Fi"

    return None


def normalize_resolution(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    replacements = {

        "Full HD":
            "1920 x 1080",

        "FHD":
            "1920 x 1080",

        "HD+":
            "1600 x 900"
    }

    if value in replacements:
        return replacements[value]

    match = re.search(
        r"(\d{3,4})\s*[xX×]\s*(\d{3,4})",
        value
    )

    if not match:
        return None

    width = match.group(1)
    height = match.group(2)

    return (
        f"{width} x {height}"
    )


def normalize_screen_size(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.lower()

    match = re.search(
        r"(\d+(\.\d+)?)",
        value
    )

    if not match:
        return None

    number = float(
        match.group(1)
    )

    if number <= 0:
        return None

    return str(number)


def normalize_cpu_model(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.replace(
        "®",
        ""
    )

    value = value.replace(
        "™",
        ""
    )

    value = value.strip()

    ambiguous_values = {

        "Intel",
        "Intel Mobile CPU",
        "Intel Pentium",
        "Intel Celeron",
        "Intel Core i3",
        "Intel Core i5",
        "Intel Core Ultra 7",
        "Intel Core i5 13th Gen",
        "Intel Core 5 Series 1",
        "Intel Core 3 Series 1",
        "Core i5",
        "Core i5 Family",
        "Core i7 Family",
        "Celeron",
        "AMD Ryzen 5",
        "AMD Ryzen 7",
        "Ryzen 5",
        "Snapdragon",
        "Snapdragon X",
        "Snapdragon X Plus",
        "Snapdragon X Elite",
        "Qualcomm Snapdragon X",
        "Qualcomm Snapdragon X Elite",
        "AMD R Series",
        "AMD Ryzen AI 300 Series",
        "AMD Ryzen 7000 Series Processor",
        "AMD Ryzen 5 7000 Series",
        "AMD Ryzen 7 7000 Series",
        "AMD Ryzen 5 8000 Series",
        "AMD Ryzen 7 5000 Series",
        "AMD Ryzen 7 2000 Series",
        "Intel 13th Generation Core i7",
        "Intel 13th Generation Core i5",
        "Intel 12th Generation Core i7",
        "Latest AMD Ryzen or Intel Core processors",
        "Intel Celeron and Pentium processors",
        "up to AMD Ryzen AI 7 Series Processors",
        "Up to AMD Ryzen AI 78",
        "10-core CPU",
        "10-Cores",
        "10",
        "2"
    }

    if value in ambiguous_values:
        return None

    replacements = {

        "1355U":
            "Intel Core i7-1355U",

        "Core i7-1355U":
            "Intel Core i7-1355U",

        "Intel Core i7-1355U (up to 5.0 GHz, 12 MB L3 cache, 10 cores, 12 threads)":
            "Intel Core i7-1355U",

        "1334U":
            "Intel Core i5-1334U",

        "Core i5-1334U":
            "Intel Core i5-1334U",

        "1335U":
            "Intel Core i5-1335U",

        "120U":
            "Intel Core 5 120U",

        "165U":
            "Intel Core Ultra 5 165U",

        "225U":
            "Intel Core Ultra 5 225U",

        "226V":
            "Intel Core Ultra 5 226V",

        "Intel Core Ultra 5 226V":
            "Intel Core Ultra 5 226V",

        "255U":
            "Intel Core Ultra 7 255U",

        "256V":
            "Intel Core Ultra 7 256V",

        "Intel Core Ultra 7 256V (2.2GHz)":
            "Intel Core Ultra 7 256V",

        "Intel Core Ultra 7 256V":
            "Intel Core Ultra 7 256V",

        "Intel Core Ultra 7 258V":
            "Intel Core Ultra 7 258V",

        "258V":
            "Intel Core Ultra 7 258V",

        "288V":
            "Intel Core Ultra 9 288V",

        "Intel Core(TM) Ultra 9 288V":
            "Intel Core Ultra 9 288V",

        "285H":
            "Intel Core Ultra 9 285H",

        "Intel Core Ultra 9 285HX":
            "Intel Core Ultra 9 285HX",

        "13420H":
            "Intel Core i5-13420H",

        "1255U":
            "Intel Core i5-1255U",

        "Intel Core i5-1035G1":
            "Intel Core i5-1035G1",

        "Intel Core i5-1145G7 vPRO":
            "Intel Core i5-1145G7 vPRO",

        "Intel Core i7-13620H":
            "Intel Core i7-13620H",

        "N200":
            "Intel Processor N200",

        "Intel Processor N200":
            "Intel Processor N200",

        "N150":
            "Intel Processor N150",

        "Intel N150":
            "Intel Processor N150",

        "Intel Processor N150":
            "Intel Processor N150",

        "N305":
            "Intel Core i3-N305",

        "Intel Core i3-N305":
            "Intel Core i3-N305",

        "N355":
            "Intel Processor N355",

        "N4500":
            "Intel Celeron N4500",

        "Intel Celeron N4500":
            "Intel Celeron N4500",

        "Intel Celeron N4500, 1.1 GHz, Up to 2.8 GHz":
            "Intel Celeron N4500",

        "Intel Celeron N4500 (1.1GHz)":
            "Intel Celeron N4500",

        "N6000":
            "Intel Pentium Silver N6000",

        "Intel Pentium Silver N6000":
            "Intel Pentium Silver N6000",

        "Intel Pentium Silver N6000 Processor (1.10 GHz up to 3.30 GHz)":
            "Intel Pentium Silver N6000",

        "7730U":
            "AMD Ryzen 7 7730U",

        "Ryzen 7-7730U":
            "AMD Ryzen 7 7730U",

        "AMD Ryzen 7 7730U":
            "AMD Ryzen 7 7730U",

        "AMD Ryzen 7 7730U 2.0GHz":
            "AMD Ryzen 7 7730U",

        "7430U":
            "AMD Ryzen 5 7430U",

        "AMD Ryzen 5 7430U":
            "AMD Ryzen 5 7430U",

        "7520U":
            "AMD Ryzen 5 7520U",

        "AMD Ryzen 5 7520U":
            "AMD Ryzen 5 7520U",

        "AMD Ryzen 5 7520U 2.8GHz":
            "AMD Ryzen 5 7520U",

        "AMD Ryzen 5 7520U Processor (2.80 GHz up to 4.30 GHz)":
            "AMD Ryzen 5 7520U",

        "7530U":
            "AMD Ryzen 5 7530U",

        "AMD Ryzen 5 7530U (up to 4.5 GHz max boost clock, 16 MB L3 cache, 6 cores, 12 threads)":
            "AMD Ryzen 5 7530U",

        "7535HS":
            "AMD Ryzen 5 7535HS",

        "7735U":
            "AMD Ryzen 7 7735U",

        "AMD Ryzen 7 7735U":
            "AMD Ryzen 7 7735U",

        "5500U":
            "AMD Ryzen 5 5500U",

        "5825U":
            "AMD Ryzen 7 5825U",

        "AMD Ryzen 7 5825U":
            "AMD Ryzen 7 5825U",

        "AMD Ryzen 7 5825U (2.0GHz)":
            "AMD Ryzen 7 5825U",

        "8640HS":
            "AMD Ryzen 5 8640HS",

        "AMD Ryzen 5 8640HS":
            "AMD Ryzen 5 8640HS",

        "7445HS":
            "AMD Ryzen 5 7445HS",

        "3000U":
            "AMD 3000U",

        "250":
            "AMD Ryzen 7 250",

        "AMD Ryzen 7 250":
            "AMD Ryzen 7 250",

        "330":
            "AMD Ryzen AI 5 330",

        "AI 7 350":
            "AMD Ryzen AI 7 350",

        "AMD Ryzen AI 7 350":
            "AMD Ryzen AI 7 350",

        "AMD Ryzen AI 7 353":
            "AMD Ryzen AI 7 353",

        "AMD Ryzen AI 5 330":
            "AMD Ryzen AI 5 330",

        "AMD Ryzen 5 AI 5 330":
            "AMD Ryzen AI 5 330",

        "Apple A18 Pro Chip":
            "Apple A18 Pro",

        "Apple A18 Pro chip":
            "Apple A18 Pro",

        "Apple A18 Pro 6-Core":
            "Apple A18 Pro",

        "Apple A18 Pro 6-Core CPU":
            "Apple A18 Pro",

        "Apple M5":
            "Apple M5 chip",

        "Apple M5 Chip":
            "Apple M5 chip",

        "Apple M5 10-Core":
            "Apple M5 chip",

        "Apple M5 10-Core Chip":
            "Apple M5 chip",

        "Apple H2 chip":
            "Apple H2 chip",

        "Apple H2 headphone chip":
            "Apple H2 chip",

        "H2 headphone chip":
            "Apple H2 chip",

        "MediaTek Kompanio 838 Processor (2.60 GHz)":
            "MediaTek Kompanio 838",

        "838":
            "MediaTek Kompanio 838",

        "MT8186":
            "MediaTek Kompanio 520",

        "520":
            "MediaTek Kompanio 520",

        "X1P-42-100":
            "Snapdragon X Plus X1P-42-100",

        "Snapdragon X Plus X1P-42-100":
            "Snapdragon X Plus X1P-42-100",

        "X1E-78-100":
            "Snapdragon X Elite X1E-78-100",

        "Snapdragon X Elite X1E-78-100":
            "Snapdragon X Elite X1E-78-100",

        "X1-26-100":
            "Snapdragon X X1-26-100"
    }

    if value in replacements:
        return replacements[value]

    return value


def normalize_gpu_model(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.replace(
        "®",
        ""
    )

    value = value.replace(
        "™",
        ""
    )

    value = value.strip()

    ambiguous_values = {

        "Intel",
        "AMD",
        "NVIDIA",
        "Qualcomm",
        "Dedicated",
        "Integrated",
        "Integrated graphics or discrete options"
    }

    if value in ambiguous_values:
        return None

    replacements = {

        "Integrated Graphics":
            "Integrated Graphics",

        "Integrated Intel Graphics":
            "Intel Graphics",

        "Integrated Intel UHD graphics":
            "Intel UHD Graphics",

        "Integrated Intel UHD Graphics":
            "Intel UHD Graphics",

        "Intel UHD graphics":
            "Intel UHD Graphics",

        "UHD Graphics":
            "Intel UHD Graphics",

        "Intel UHD Graphics":
            "Intel UHD Graphics",

        "Intel UHD Graphics 770":
            "Intel UHD Graphics 770",

        "Intel HD Graphics":
            "Intel HD Graphics",

        "Intel Graphics":
            "Intel Graphics",

        "Intel Arc":
            "Intel Arc Graphics",

        "Intel Arc Graphics":
            "Intel Arc Graphics",

        "Intel Arc Graphics 140V":
            "Intel Arc Graphics 140V",

        "Intel Arc 140V":
            "Intel Arc Graphics 140V",

        "Intel Arc 140V Graphics (8GB)":
            "Intel Arc Graphics 140V",

        "Intel Arc 130V":
            "Intel Arc Graphics 130V",

        "Intel Arc 130V Graphics":
            "Intel Arc Graphics 130V",

        "AMD Radeon":
            "AMD Radeon Graphics",

        "AMD Radeon Graphics":
            "AMD Radeon Graphics",

        "Radeon Graphics":
            "AMD Radeon Graphics",

        "Integrated: AMD Radeon Graphics":
            "AMD Radeon Graphics",

        "Integrated AMD Radeon 610M":
            "AMD Radeon 610M",

        "AMD Radeon 610M":
            "AMD Radeon 610M",

        "AMD Radeon 780M":
            "AMD Radeon 780M",

        "AMD Radeon 860M":
            "AMD Radeon 860M",

        "AMD Radeon 860M Graphics":
            "AMD Radeon 860M",

        "Up to AMD Radeon 860M Graphics":
            "AMD Radeon 860M",

        "Qualcomm Adreno":
            "Qualcomm Adreno Graphics",

        "Qualcomm Adreno GPU":
            "Qualcomm Adreno Graphics",

        "Integrated Qualcomm Adreno Graphics":
            "Qualcomm Adreno Graphics",

        "MediaTek Integrated Graphics":
            "MediaTek Integrated Graphics",

        "Integrated ARM Mali-G52 2EE MC2 GPU":
            "ARM Mali-G52 2EE MC2",

        "Integrated ARM Mali-G52 2EE MC2":
            "ARM Mali-G52 2EE MC2",

        "Integrated ARM Mali-G57 MC3 GPU":
            "ARM Mali-G57 MC3",

        "Apple A18 Pro 5-core":
            "Apple A18 Pro 5-core GPU",

        "Apple (5-Core)":
            "Apple A18 Pro 5-core GPU",

        "Integrated 5-core GPU (part of A18 Pro chip)":
            "Apple A18 Pro 5-core GPU",

        "NVIDIA GeForce RTX 4050":
            "NVIDIA GeForce RTX 4050",

        "NVIDIA GeForce RTX 5060":
            "NVIDIA GeForce RTX 5060",

        "NVIDIA GeForce RTX 2050":
            "NVIDIA GeForce RTX 2050"
    }

    if value in replacements:
        return replacements[value]

    return value


def normalize_battery_life(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    match = re.search(
        r"(\d+(\.\d+)?)",
        value
    )

    if not match:
        return None

    number = float(
        match.group(1)
    )

    if number <= 0:
        return None

    return str(number)


def normalize_weight(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    match = re.search(
        r"(\d+(\.\d+)?)",
        value
    )

    if not match:
        return None

    number = float(
        match.group(1)
    )

    if number <= 0:
        return None

    return str(
        round(number, 1)
    )


def normalize_touchscreen(value):

    value = clean_text(
        value
    )

    if value is None:
        return None

    value = value.lower()

    if value in {
        "true",
        "yes",
        "y",
        "present",
        "active",
        "touchscreen",
        "✔",
        "supports multitouch gestures",
        "1",
        "1.0"
    }:
        return "true"

    if value in {
        "false",
        "no",
        "none",
        "non-touch",
        "non-touch screen",
        "not included",
        "0",
        "0.0"
    }:
        return "false"

    return None


def canonicalize(
    attribute,
    value
):

    if value is None:
        return None

    if attribute == "bluetooth_version":

        return normalize_bluetooth(
            value
        )

    if attribute == "operating_system":

        return normalize_operating_system(
            value
        )

    if attribute == "wifi_standard":

        return normalize_wifi(
            value
        )

    if attribute == "display_resolution":

        return normalize_resolution(
            value
        )

    if attribute == "screen_size":

        return normalize_screen_size(
            value
        )

    if attribute == "cpu_model":

        return normalize_cpu_model(
            value
        )

    if attribute == "gpu_model":

        return normalize_gpu_model(
            value
        )

    if attribute == "battery_life_hr":

        return normalize_battery_life(
            value
        )

    if attribute == "weight_lb":

        return normalize_weight(
            value
        )

    if attribute == "touchscreen":

        return normalize_touchscreen(
            value
        )

    return clean_text(
        value
    )