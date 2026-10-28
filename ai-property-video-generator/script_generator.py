"""Fact-grounded rule-based script generation. No network calls or API keys."""
from typing import Iterable

def generate_scenes(property_name: str, location: str, price: str, property_type: str,
                    features: Iterable[str], cta_text: str) -> list[dict[str, str]]:
    """Return ordered video scenes using only supplied listing facts."""
    name = property_name.strip()
    location = location.strip()
    price = price.strip()
    property_type = property_type.strip()
    feature_list = [str(x).strip() for x in features if str(x).strip()]
    cta = cta_text.strip() or "Contact us for more information"
    scenes = [
        {"label": "PROPERTY INTRODUCTION",
         "caption": f"Discover {name}",
         "narration": f"Discover {name}."},
        {"label": "LOCATION",
         "caption": f"Located in {location}",
         "narration": f"Located in {location}."},
        {"label": "PROPERTY TYPE",
         "caption": property_type,
         "narration": f"Explore this {property_type}."},
    ]
    for feature in feature_list[:4]:
        scenes.append({
            "label": "PROPERTY FEATURE",
            "caption": feature,
            "narration": f"Featuring {feature.lower()}."
        })
    if price:
        scenes.append({"label": "LISTING PRICE", "caption": price,
                       "narration": f"Listed at {price}."})
    scenes.append({"label": "ENQUIRE TODAY", "caption": cta, "narration": cta + "."})
    return scenes

def validate_property(property_name: str, location: str, price: str,
                      property_type: str, features: Iterable[str], images: list) -> list[str]:
    errors = []
    for label, value in [
        ("Property name", property_name), ("Location", location),
        ("Price", price), ("Property type", property_type)
    ]:
        if not str(value or "").strip():
            errors.append(f"{label} is required.")
    feature_list = [str(x).strip() for x in features if str(x).strip()]
    if not feature_list:
        errors.append("Add at least one property feature.")
    if len(images) < 4:
        errors.append("Upload at least 4 property images.")
    if len(images) > 8:
        errors.append("Upload no more than 8 property images.")
    return errors
