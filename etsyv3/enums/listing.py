from enum import Enum


class ItemWeightUnit(Enum):
    OZ = "oz"
    LB = "lb"
    G = "g"
    KG = "kg"


class ItemDimensionsUnit(Enum):
    IN = "in"
    FT = "ft"
    MM = "mm"
    YD = "yd"
    INCHES = "inches"


class WhoMade(Enum):
    I_DID = "i_did"
    SOMEONE_ELSE = "someone_else"
    COLLECTIVE = "collective"


class WhenMade(Enum):
    MADE_TO_ORDER = "made_to_order"
    TWENTY_TWENTIES = "2020_2023"
    TWENTY_TENS = "2010_2019"
    TWENTY_OH_THREE_TO_NINE = "2003_2009"
    BEFORE_2003 = "before_2003"
    TWO_THOUSAND_TO_TWO = "2000_2002"
    NINETEEN_NINETIES = "1990s"
    NINETEEN_EIGHTIES = "1980s"
    NINETEEN_SEVENTIES = "1970s"
    NINETEEN_SIXTIES = "1960s"
    NINETEEN_FIFTIES = "1950s"
    NINETEEN_FORTIES = "1940s"
    NINETEEN_THIRTIES = "1930s"
    NINETEEN_TWENTIES = "1920s"
    NINETEEN_TENS = "1910s"
    NINETEEN_HUNDREDS = "1900s"
    EIGHTEEN_HUNDREDS = "1800s"
    SEVENTEEN_HUNDREDS = "1700s"
    BEFORE_1700 = "before_1700"


class ListingRequestState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ListingType(Enum):
    PHYSICAL = "physical"
    DOWNLOAD = "download"
    BOTH = "both"
