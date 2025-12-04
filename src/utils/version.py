# application version management
from __future__ import annotations

import re
from typing import NamedTuple


class Version(NamedTuple):
    # semantic version representation
    major: int
    minor: int
    patch: int
    
    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        # parse version from string like '1.2.3'
        pattern = r'^(\d+)\.(\d+)\.(\d+)$'
        match = re.match(pattern, version_str.strip())
        if not match:
            raise ValueError(f"Formato de version invalido: {version_str}")
        
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3))
        )
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __gt__(self, other: 'Version') -> bool:
        # check if this version is greater than another
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __eq__(self, other: 'Version') -> bool:
        # check if versions are equal
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


# current application version
CURRENT_VERSION = Version(1, 0, 8)

# update configuration
UPDATE_CONFIG = {
    "check_url": "https://api.github.com/repos/chaseG20gam/Integra-App/releases/latest",
    "download_base_url": "https://github.com/chaseG20gam/Integra-App/releases/download/",
    "user_agent": f"Integra-Client-Manager/{CURRENT_VERSION}",
    "test_mode": False  # set to false when you have actual releases
}