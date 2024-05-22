from datetime import datetime

from pydantic import BaseModel

# # Shared properties
# class StrongBase(BaseModel):
#     time_info: str
#     data: dict


# # Shared properties
# class WeakBase(BaseModel):
#     time_info: str
#     data: dict


# Properties to receive on item creation
class StrengthsPublic(BaseModel):
    # strong: dict[str, dict[str, dict[str, float]]] | None = None
    # weak: dict[str, dict[str, dict[str, float]]] | None = None
    strong: dict[datetime, dict[str, float]] | None = None
    weak: dict[datetime, dict[str, float]] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "strong": {
                        "2023-11-20T00:00:00-05:00": {
                            "XLK": 1.0050949160676566,
                            "b_mark": 1.0269030414615252,
                        },
                        "2023-11-21T00:00:00-05:00": {
                            "XLK": 1.0050949160676566,
                            "b_mark": 1.0263760235208932,
                        },
                        "2023-11-22T00:00:00-05:00": {
                            "XLK": 1.0050949160676566,
                            "b_mark": 1.0302234572653284,
                        },
                    },
                    "weak": {
                        "2023-11-20T00:00:00-05:00": {
                            "XLK": 1.0050949160676566,
                            "XLY": 1.010876490415112,
                            "XLC": 1.004108488162251,
                            "XLE": 0.983529063818153,
                            "XLB": 1.0148305526552135,
                            "XLP": 0.9877981862719292,
                            "XLV": 0.9896279783724378,
                            "XLI": 1.0040467286566654,
                            "b_mark": 1.0269030414615252,
                        },
                        "2023-11-21T00:00:00-05:00": {
                            "XLK": 1.0055814381614032,
                            "XLY": 1.0092801952425072,
                            "XLC": 1.005909568539329,
                            "XLE": 0.9816228108424745,
                            "XLB": 1.0162184761697521,
                            "XLP": 0.9855385516396638,
                            "XLV": 0.991041761827697,
                            "XLI": 1.0046309983412018,
                            "b_mark": 1.0263760235208932,
                        },
                        "2023-11-22T00:00:00-05:00": {
                            "XLK": 1.006476022976499,
                            "XLY": 1.007826256859914,
                            "XLC": 1.008148241982169,
                            "XLE": 0.9797772823556082,
                            "XLB": 1.0166074789634105,
                            "XLP": 0.9828771494025098,
                            "XLV": 0.9930171169975734,
                            "XLI": 1.0049985590285555,
                            "b_mark": 1.0302234572653284,
                        },
                    },
                }
            ]
        }
    }
