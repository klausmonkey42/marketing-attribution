"""
Phone number validation and normalization utilities.

This module provides functions for validating and normalizing North American
phone numbers, including area code validation against official NANPA registry.
"""

import re
from typing import Optional
from functools import lru_cache


# Valid US/Canadian area codes (NANPA)
# Source: https://www.nationalnanpa.com/enas/geoAreaCodeNumberReport.do
VALID_AREA_CODES = {
    201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 212, 213, 214, 215, 216, 217, 218, 219,
    220, 223, 224, 225, 226, 228, 229, 231, 234, 236, 239, 240, 242, 246, 248, 249, 250, 251,
    252, 253, 254, 256, 260, 262, 264, 267, 268, 269, 270, 272, 276, 279, 281, 284, 289, 301,
    302, 303, 304, 305, 306, 307, 308, 309, 310, 312, 313, 314, 315, 316, 317, 318, 319, 320,
    321, 323, 325, 330, 331, 332, 334, 336, 337, 339, 340, 341, 343, 345, 346, 347, 351, 352,
    360, 361, 364, 365, 367, 380, 385, 386, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,
    412, 413, 414, 415, 416, 417, 418, 419, 423, 424, 425, 430, 431, 432, 434, 435, 437, 438,
    440, 441, 442, 443, 445, 450, 458, 463, 469, 470, 473, 475, 478, 479, 480, 484, 501, 502,
    503, 504, 505, 506, 507, 508, 509, 510, 512, 513, 514, 515, 516, 517, 518, 519, 520, 530,
    531, 534, 539, 540, 541, 548, 551, 559, 561, 562, 563, 564, 567, 570, 571, 573, 574, 575,
    579, 580, 581, 585, 586, 587, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 612, 613,
    614, 615, 616, 617, 618, 619, 620, 623, 626, 628, 629, 630, 631, 636, 639, 640, 641, 646,
    647, 649, 650, 651, 657, 658, 660, 661, 662, 664, 667, 669, 670, 671, 672, 678, 680, 681,
    682, 684, 689, 701, 702, 703, 704, 705, 706, 707, 708, 709, 712, 713, 714, 715, 716, 717,
    718, 719, 720, 721, 724, 725, 726, 727, 731, 732, 734, 737, 740, 743, 747, 754, 757, 758,
    760, 762, 763, 765, 767, 769, 770, 772, 773, 774, 775, 778, 779, 780, 781, 782, 784, 785,
    786, 787, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 812, 813, 814, 815, 816, 817,
    818, 819, 820, 825, 828, 829, 830, 831, 832, 838, 843, 845, 847, 848, 849, 850, 854, 856,
    857, 858, 859, 860, 862, 863, 864, 865, 867, 868, 869, 870, 872, 873, 876, 878, 901, 902,
    903, 904, 905, 906, 907, 908, 909, 910, 912, 913, 914, 915, 916, 917, 918, 919, 920, 925,
    928, 929, 930, 931, 934, 936, 937, 938, 939, 940, 941, 947, 949, 951, 952, 954, 956, 959,
    970, 971, 972, 973, 978, 979, 980, 984, 985, 986, 989
}


def strip_non_numeric(phone: str) -> str:
    """
    Remove all non-numeric characters from a phone number.
    
    Args:
        phone: Input phone number string
        
    Returns:
        String containing only numeric digits
        
    Example:
        >>> strip_non_numeric("(555) 123-4567")
        '5551234567'
    """
    if not phone:
        return ""
    return re.sub(r'[^0-9]', '', str(phone))


@lru_cache(maxsize=10000)
def is_valid_phone(phone: str) -> bool:
    """
    Validate if a phone number is a valid 10-digit North American number.
    
    Checks:
    1. Contains exactly 10 digits after normalization
    2. Area code (first 3 digits) is in valid NANPA registry
    
    Results are cached for performance on repeated validations.
    
    Args:
        phone: Phone number to validate (any format)
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_phone("(619) 555-1234")
        True
        >>> is_valid_phone("(999) 555-1234")  # Invalid area code
        False
        >>> is_valid_phone("555-1234")  # Too short
        False
    """
    if not phone:
        return False
        
    numeric_phone = strip_non_numeric(phone)
    
    # Check length
    if len(numeric_phone) != 10:
        return False
    
    # Check area code
    try:
        area_code = int(numeric_phone[:3])
        return area_code in VALID_AREA_CODES
    except (ValueError, IndexError):
        return False


def normalize_phone(phone: str, add_country_code: bool = True) -> Optional[str]:
    """
    Normalize a phone number to standard format.
    
    Args:
        phone: Input phone number (any format)
        add_country_code: If True, prepends '1' for North American numbers
        
    Returns:
        Normalized phone number string, or None if invalid
        
    Example:
        >>> normalize_phone("(619) 555-1234")
        '16195551234'
        >>> normalize_phone("(619) 555-1234", add_country_code=False)
        '6195551234'
        >>> normalize_phone("invalid")
        None
    """
    if not is_valid_phone(phone):
        return None
    
    normalized = strip_non_numeric(phone)
    
    if add_country_code and not normalized.startswith('1'):
        normalized = '1' + normalized
    
    return normalized


def format_phone_display(phone: str) -> str:
    """
    Format a phone number for display.
    
    Args:
        phone: Normalized phone number (10 digits)
        
    Returns:
        Formatted phone number in (XXX) XXX-XXXX format
        
    Example:
        >>> format_phone_display("6195551234")
        '(619) 555-1234'
    """
    numeric = strip_non_numeric(phone)
    
    if len(numeric) == 10:
        return f"({numeric[:3]}) {numeric[3:6]}-{numeric[6:]}"
    elif len(numeric) == 11 and numeric[0] == '1':
        return f"+1 ({numeric[1:4]}) {numeric[4:7]}-{numeric[7:]}"
    
    return phone


def phones_match(phone1: str, phone2: str) -> bool:
    """
    Check if two phone numbers match after normalization.
    
    Args:
        phone1: First phone number
        phone2: Second phone number
        
    Returns:
        True if numbers match, False otherwise
        
    Example:
        >>> phones_match("(619) 555-1234", "619-555-1234")
        True
        >>> phones_match("(619) 555-1234", "(858) 555-1234")
        False
    """
    norm1 = normalize_phone(phone1, add_country_code=False)
    norm2 = normalize_phone(phone2, add_country_code=False)
    
    if norm1 is None or norm2 is None:
        return False
    
    return norm1 == norm2


# Clear cache function for testing
def clear_validation_cache():
    """Clear the phone validation cache."""
    is_valid_phone.cache_clear()
