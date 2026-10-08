"""Seed data. Runs automatically on startup when the DB is empty, or manually:

    python -m app.seed

Add the remaining species by appending dicts to SEED (taxonomy counts vary by source;
18 is the commonly cited number). Replace placeholder image URLs with images you are
licensed to use (e.g. Wikimedia Commons, CC-licensed).
"""
import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal, init_db
from app.models import Penguin, PenguinFact


def _img(label: str) -> str:
    return f"https://placehold.co/800x600/png?text={label.replace(' ', '+')}"


SEED: list[dict] = [
    {
        "id": "emperor",
        "common_name": "Emperor Penguin",
        "scientific_name": "Aptenodytes forsteri",
        "height_cm": 115, "weight_kg": 30,
        "conservation_status": "Near Threatened",
        "diet": "Fish, krill and squid",
        "habitat": "Antarctic sea ice and surrounding waters",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Penguin_in_Antarctica_jumping_out_of_the_water.jpg?width=800",
        "facts": [
            "Males incubate the single egg on their feet through the Antarctic winter.",
            "Emperors can dive to more than 500 metres in search of food.",
        ],
    },
    {
        "id": "adelie",
        "common_name": "Adélie Penguin",
        "scientific_name": "Pygoscelis adeliae",
        "height_cm": 70, "weight_kg": 4.5,
        "conservation_status": "Least Concern",
        "diet": "Mostly Antarctic krill, plus small fish",
        "habitat": "Rocky Antarctic coastlines and pack ice",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Adelie_penguins_in_the_South_Shetland_Islands.jpg?width=800",
        "facts": [
            "Adélies build nests out of small stones, and stones are prized currency.",
            "They toboggan across the ice on their bellies to travel faster.",
        ],
    },
    {
        "id": "little-blue",
        "common_name": "Little Blue Penguin",
        "scientific_name": "Eudyptula minor",
        "height_cm": 33, "weight_kg": 1.2,
        "conservation_status": "Least Concern",
        "diet": "Small schooling fish, squid and crustaceans",
        "habitat": "Coastal burrows around southern Australia and New Zealand",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Eudyptula_novaehollandiae_family_exiting_burrow.jpg?width=800",
        "facts": [
            "It is the smallest penguin species in the world.",
            "Colonies return from sea together at dusk, as in Phillip Island's famous Penguin Parade.",
        ],
    },
    {
        "id": "king",
        "common_name": "King Penguin",
        "scientific_name": "Aptenodytes patagonicus",
        "height_cm": 90,
        "weight_kg": 15.0,
        "conservation_status": "Least Concern",
        "diet": "Lanternfish, squid and crustaceans",
        "habitat": "Sub-Antarctic islands and ice-free beaches",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Königspinguine_(Aptenodytes_patagonicus)_(3).jpg?width=800",
        "facts": [
            "King Penguin chicks are covered in thick brown fluff and were once believed to be a separate species called the Oakum Boy.",
            "Their breeding cycle takes 14 to 16 months, so they raise only two chicks every three years.",
        ],
    },
    {
        "id": "chinstrap",
        "common_name": "Chinstrap Penguin",
        "scientific_name": "Pygoscelis antarcticus",
        "height_cm": 72,
        "weight_kg": 4.5,
        "conservation_status": "Least Concern",
        "diet": "Antarctic krill, small fish and shrimp",
        "habitat": "Antarctic peninsula and South Atlantic sub-Antarctic islands",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Pygoscelis_antarcticus_on_the_Half_Moon_Island_02.jpg?width=800",
        "facts": [
            "Named for the narrow black band of feathers under its chin that looks like a helmet strap.",
            "They take thousands of micro-sleeps lasting only 4 seconds each to stay alert against predators.",
        ],
    },
    {
        "id": "gentoo",
        "common_name": "Gentoo Penguin",
        "scientific_name": "Pygoscelis papua",
        "height_cm": 76,
        "weight_kg": 5.5,
        "conservation_status": "Least Concern",
        "diet": "Krill, small fish and squid",
        "habitat": "Sub-Antarctic islands and the Antarctic Peninsula",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Gentoo_Penguin_at_Cooper_Bay,_South_Georgia.jpg?width=800",
        "facts": [
            "Gentoo penguins are the fastest underwater swimmers among all birds, reaching speeds up to 36 km/h (22 mph).",
            "They are recognized by the bright white bonnet-like stripe extending across the top of their head.",
        ],
    },
    {
        "id": "magellanic",
        "common_name": "Magellanic Penguin",
        "scientific_name": "Spheniscus magellanicus",
        "height_cm": 70,
        "weight_kg": 4.0,
        "conservation_status": "Least Concern",
        "diet": "Cuttlefish, squid, krill and various small fish",
        "habitat": "Coastal Argentina, Chile and the Falkland Islands",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/MagellanicPenguin.jpg?width=800",
        "facts": [
            "Named after Ferdinand Magellan, who spotted them in 1520 during his circumnavigation voyage.",
            "They shed feathers around their eyes when overheated to radiate excess body heat into the air.",
        ],
    },
    {
        "id": "humboldt",
        "common_name": "Humboldt Penguin",
        "scientific_name": "Spheniscus humboldti",
        "height_cm": 68,
        "weight_kg": 4.2,
        "conservation_status": "Vulnerable",
        "diet": "Anchovies, sardines and small schooling fish",
        "habitat": "Arid coastal Pacific regions of Peru and Chile",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/HumboldtPenguins.jpg?width=800",
        "facts": [
            "They nest by burrowing into thick layers of dried bat and seabird dung (guano).",
            "A fleshy, featherless pink patch at the base of their bill acts as a cooling system in warm weather.",
        ],
    },
    {
        "id": "galapagos",
        "common_name": "Galápagos Penguin",
        "scientific_name": "Spheniscus mendiculus",
        "height_cm": 49,
        "weight_kg": 2.5,
        "conservation_status": "Endangered",
        "diet": "Small fish such as mullet and sardines, plus crustaceans",
        "habitat": "Galápagos Islands, Ecuador",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Galapagos_penguin_(Spheniscus_mendiculus)_-Isabela2.jpg?width=800",
        "facts": [
            "It is the only penguin species that lives north of the Equator in the wild.",
            "To keep cool, they pant like dogs and swim in cold currents brought by the Cromwell Current.",
        ],
    },
    {
        "id": "african",
        "common_name": "African Penguin",
        "scientific_name": "Spheniscus demersus",
        "height_cm": 60,
        "weight_kg": 3.0,
        "conservation_status": "Endangered",
        "diet": "Anchovies, pilchards, sardines and small crustaceans",
        "habitat": "South-western coast of Africa and offshore islands",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/African_penguins_at_Boulders_Beach_01.jpg?width=800",
        "facts": [
            "Also known as the 'Jackass Penguin' because of its loud, donkey-like braying call.",
            "Pink glands above their eyes become darker pink as the penguin gets hotter to cool down body temperature.",
        ],
    },
    {
        "id": "yellow-eyed",
        "common_name": "Yellow-eyed Penguin",
        "scientific_name": "Megadyptes antipodes",
        "height_cm": 65,
        "weight_kg": 5.5,
        "conservation_status": "Endangered",
        "diet": "Small to medium surface and bottom-dwelling fish, and squid",
        "habitat": "Coastal forests and scrublands of southern New Zealand and sub-Antarctic islands",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Yellow_Eyed_Penguin._(Megadyptes_antipodes)_(9868019174).jpg?width=800",
        "facts": [
            "Known locally by its Māori name 'Hoiho', which means 'noise shouter'.",
            "Unlike most colonial penguins, Yellow-eyed penguins nest out of sight of one another in coastal forests.",
        ],
    },
    {
        "id": "fiordland",
        "common_name": "Fiordland Penguin",
        "scientific_name": "Eudyptes pachyrhynchus",
        "height_cm": 60,
        "weight_kg": 3.7,
        "conservation_status": "Vulnerable",
        "diet": "Squid, octopus, krill and small fish",
        "habitat": "Dense rainforests and rocky sea caves of South Island, New Zealand",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fiordland_Crested_Penguin_-_Stewart Island_-_New Zealand_(39070132111).jpg?width=800",
        "facts": [
            "One of the few penguin species that nests in temperate rainforests among thick vegetation.",
            "They have distinctive white stripes on their cheeks beneath yellow crest plumes.",
        ],
    },
    {
        "id": "snares",
        "common_name": "Snares Penguin",
        "scientific_name": "Eudyptes robustus",
        "height_cm": 60,
        "weight_kg": 3.0,
        "conservation_status": "Vulnerable",
        "diet": "Krill, small squid and fish",
        "habitat": "Snares Islands off the southern coast of New Zealand",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Snares_Penguin,_Southland,_NZ-SO,_NZ_imported_from_iNaturalist_photo_462871455.jpg?width=800",
        "facts": [
            "Breeds exclusively on the tiny Snares Islands group, making its range one of the smallest of any penguin.",
            "They nest in colonies beneath tree canopies or among dense Olearia forests.",
        ],
    },
    {
        "id": "erect-crested",
        "common_name": "Erect-crested Penguin",
        "scientific_name": "Eudyptes sclateri",
        "height_cm": 67,
        "weight_kg": 4.2,
        "conservation_status": "Endangered",
        "diet": "Pelagic fish, krill and squid",
        "habitat": "Bounty and Antipodes Islands of New Zealand",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Eudyptes_sclateri_129036290.jpg?width=800",
        "facts": [
            "They are able to raise and lower their bright yellow crest feathers upright at will.",
            "Females habitually lay two eggs but almost always abandon or discard the smaller first egg.",
        ],
    },
    {
        "id": "macaroni",
        "common_name": "Macaroni Penguin",
        "scientific_name": "Eudyptes chrysolophus",
        "height_cm": 70,
        "weight_kg": 5.5,
        "conservation_status": "Vulnerable",
        "diet": "Krill, small crustaceans, fish and squid",
        "habitat": "Sub-Antarctic islands and the Antarctic Peninsula",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Macaroni_Penguin_(Eudyptes_chrysolophus)6.jpg?width=800",
        "facts": [
            "Named by 18th-century English sailors after 'Macaroni' fashion due to their flashy yellow head plumes.",
            "It is the most abundant penguin species in the world, with millions of breeding pairs.",
        ],
    },
    {
        "id": "royal",
        "common_name": "Royal Penguin",
        "scientific_name": "Eudyptes schlegeli",
        "height_cm": 72,
        "weight_kg": 5.5,
        "conservation_status": "Near Threatened",
        "diet": "Krill, small fish and squid",
        "habitat": "Macquarie Island and neighboring islets in the Southern Ocean",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/RoyalPenguins2.JPG?width=800",
        "facts": [
            "Closely related to Macaroni penguins, but distinguished by their white or pale grey faces.",
            "They nest exclusively on sub-Antarctic Macquarie Island and surrounding rocky islets.",
        ],
    },
    {
        "id": "southern-rockhopper",
        "common_name": "Southern Rockhopper Penguin",
        "scientific_name": "Eudyptes chrysocome",
        "height_cm": 52,
        "weight_kg": 2.7,
        "conservation_status": "Vulnerable",
        "diet": "Krill, squid, octopus, lanternfish and crustaceans",
        "habitat": "Rocky coasts of sub-Antarctic islands in the South Atlantic and Indian Oceans",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Rockhopper_Penguin_(5566888870).jpg?width=800",
        "facts": [
            "Instead of waddling or sliding, they navigate steep cliff sides by hopping from boulder to boulder.",
            "They aggressively defend their nests using bill-jabbing and loud harsh calls.",
        ],
    },
    {
        "id": "northern-rockhopper",
        "common_name": "Northern Rockhopper Penguin",
        "scientific_name": "Eudyptes moseleyi",
        "height_cm": 55,
        "weight_kg": 2.5,
        "conservation_status": "Endangered",
        "diet": "Krill, crustaceans, squid and small fish",
        "habitat": "Tristan da Cunha and Gough Island in the South Atlantic Ocean",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Northern_Rockhopper_Penguin_on_Inaccessible_Island.jpg?width=800",
        "facts": [
            "Features significantly longer, more dramatic yellow plumes than the Southern Rockhopper.",
            "More than 99% of their global population is restricted to Tristan da Cunha and Gough Island.",
        ],
    },
]


async def seed_if_empty(session: AsyncSession) -> bool:
    """Insert SEED data only if the table is empty. Returns True if anything was inserted."""
    count = await session.scalar(select(func.count()).select_from(Penguin))
    if count:
        return False
    for item in SEED:
        data = {k: v for k, v in item.items() if k != "facts"}
        penguin = Penguin(**data)
        penguin.facts = [PenguinFact(text=t) for t in item["facts"]]
        session.add(penguin)
    await session.commit()
    return True


async def _main() -> None:
    await init_db()
    async with SessionLocal() as session:
        inserted = await seed_if_empty(session)
    print("Seeded database." if inserted else "Database already has data; nothing to do.")


if __name__ == "__main__":
    asyncio.run(_main())
