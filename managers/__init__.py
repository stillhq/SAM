from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict

from sam.actions import Action


# IMPORTED FROM SADB TO PREVENT DEPENDENCE
class MobileType(Enum):
    """
    Enum representing the type of mobile support for an app.

    Attributes:
        UNKNOWN (int): Unknown mobile support.
        PC_ONLY (int): App supports only PC.
        MOBILE_ONLY (int): App supports only mobile.
        HYBRID (int): App supports both PC and mobile.
    """
    UNKNOWN = 0
    PC_ONLY = 1
    MOBILE_ONLY = 2
    HYBRID = 3


class Pricing(Enum):
    """
    Enum representing the pricing model of an app.

    Attributes:
        UNKNOWN (int): Unknown pricing model.
        FREE (int): App is free.
        FREE_WITH_ADS (int): App is free with ads.
        FREE_WITH_IN_APP_PURCHASES (int): App is free with in-app purchases.
        FREEMIUM (int): App is freemium.
        ONE_TIME (int): App has a one-time purchase cost.
        SUBSCRIPTION (int): App has a subscription cost.
        EXTERNAL_SUBSCRIPTION (int): App has an external subscription cost.
    """
    UNKNOWN = 0
    FREE = 1
    FREE_WITH_ADS = 2
    FREE_WITH_IN_APP_PURCHASES = 3
    FREEMIUM = 4
    ONE_TIME = 5
    SUBSCRIPTION = 6
    EXTERNAL_SUBSCRIPTION = 7


class StillRating(Enum):
    """
    Enum representing the still rating of an app.

    Attributes:
        UNKNOWN (int): Unknown still rating.
        WARNING (int): Still rating of 1.
        BRONZE (int): Still rating of 2.
        SILVER (int): Still rating of 3.
        GOLD (int): Still rating of 4.
        GOLD_PLUS (int): Still rating of 5.
    """
    UNKNOWN = 0
    WARNING = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    GOLD_PLUS = 5


# Used in some cases when sadb.App doesn't have data (sideloaded apps for example)
class UnknownApp():
    app_id: str = "unknown"
    name: str
    primary_src: str
    src_pkg_name: str
    icon_url: str
    author: str
    summary: str
    description: str
    keywords: List[str] = []
    mimetypes: List[str] = []
    app_license: str = "Unknown"
    pricing: Pricing = Pricing.UNKNOWN
    mobile: MobileType = MobileType.UNKNOWN
    still_rating: StillRating = StillRating.UNKNOWN
    still_rating_notes: str = ""
    homepage: str = ""
    donate_url: str = ""
    screenshot_urls: List[str] = []
    demo_url: str = ""
    addons: List[str] = []


class Manager(ABC):
    title: str
    manager_id: str
    current_action = Action

    def __init__(self, title: str, manager_id: str):
        self.title = title
        self.manager_id = manager_id

    @property
    @abstractmethod
    def manager_type(self) -> str:  # Hardcoded property
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def install(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def remove(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def update(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_update(self, package: str) -> bool:
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_updates(self) -> List[str]:
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_installed(self) -> List[str]:
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def bare_app_info(self, app_name: str) -> dict:
        raise NotImplementedError("Not implemented for manager type")
