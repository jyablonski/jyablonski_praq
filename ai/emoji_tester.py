"""
Batched emoji classifier for news headlines.
Sends batches of headlines to OpenAI and returns one emoji per headline.
"""

import asyncio
import logging
import os
from typing import Iterable

import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODEL = "openai/gpt-5.4-nano"
BATCH_SIZE = 150
CONCURRENCY = 8
DEFAULT_EMOJI = "📰"

SYSTEM_PROMPT = """\
You assign a single, context-aware emoji to each news headline.

Rules:
- Return exactly one emoji per headline.
- Pick the most semantically specific emoji available. Prefer 🏀 for an NBA story over 🏟️.
- Do NOT use 📰 or 🗞️ unless the headline is genuinely about the news industry itself.
- Reflect the subject matter, not the sentiment.
- Match each output to its input by id.
"""


class HeadlineEmoji(BaseModel):
    id: str
    emoji: str = Field(min_length=1, max_length=8)

    @field_validator("emoji")
    @classmethod
    def must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("emoji cannot be empty")
        return v.strip()


class BatchResponse(BaseModel):
    assignments: list[HeadlineEmoji]


client = instructor.from_provider(
    MODEL,
    async_client=True,
    api_key=os.environ["OPENAI_TEST_KEY"],
)


def chunk(seq: list, size: int) -> Iterable[list]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def format_batch(headlines: list[dict]) -> str:
    lines = [f"{h['id']}: {h['headline']}" for h in headlines]
    return "\n".join(lines)


async def classify_batch(
    headlines: list[dict], semaphore: asyncio.Semaphore
) -> dict[str, str]:
    """Classify one batch. Returns {id: emoji}. Falls back to default on failure."""
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                response_model=BatchResponse,
                max_retries=2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Assign one emoji to each headline below. "
                            "Return an assignment for every id.\n\n"
                            f"{format_batch(headlines)}"
                        ),
                    },
                ],
            )
        except Exception as e:
            logger.warning(f"Batch failed, using default emoji: {e}")
            return {h["id"]: DEFAULT_EMOJI for h in headlines}

    result = {a.id: a.emoji for a in response.assignments}

    for h in headlines:
        if h["id"] not in result:
            logger.warning(f"Missing assignment for {h['id']}, using default")
            result[h["id"]] = DEFAULT_EMOJI

    return result


async def classify_all(headlines: list[dict]) -> dict[str, str]:
    semaphore = asyncio.Semaphore(CONCURRENCY)
    batches = list(chunk(headlines, BATCH_SIZE))
    logger.info(f"Classifying {len(headlines)} headlines in {len(batches)} batches")

    tasks = [classify_batch(batch, semaphore) for batch in batches]
    results = await asyncio.gather(*tasks)

    merged = {}
    for r in results:
        merged.update(r)
    return merged


SAMPLE_HEADLINES = [
    "Fed holds rates steady amid persistent inflation concerns",
    "Lakers extend winning streak to seven games behind LeBron triple-double",
    "SpaceX Starship completes successful orbital test flight",
    "Wildfires force evacuations across northern California",
    "New study links gut bacteria to mood regulation",
    "Apple unveils foldable iPhone prototype at developer conference",
    "Hurricane Marcus makes landfall in Florida Panhandle",
    "Taylor Swift announces surprise album drop at midnight",
    "Boeing 737 makes emergency landing after engine failure",
    "Nvidia stock surges 12% on record AI chip demand",
    "Manchester United fires manager after string of losses",
    "Scientists discover new species of deep-sea octopus",
    "Senate passes bipartisan infrastructure bill",
    "Massive data breach exposes 50 million user records",
    "Drought conditions worsen across the American Southwest",
    "Netflix raises subscription prices for premium tier",
    "Earthquake of magnitude 6.2 strikes coastal Japan",
    "Tesla recalls 200,000 vehicles over software defect",
    "WHO declares end to mpox public health emergency",
    "Pope Francis hospitalized for respiratory infection",
    "Chiefs defeat Bills in overtime AFC championship thriller",
    "OpenAI releases new reasoning model with multimodal capabilities",
    "FDA approves first oral treatment for postpartum depression",
    "Russia and Ukraine resume peace negotiations in Geneva",
    "Major airline reports record summer travel bookings",
    "Researchers develop battery that lasts 50% longer",
    "Coffee prices hit ten-year high amid Brazilian frost",
    "Marvel announces three new films for next phase",
    "Court overturns conviction in landmark privacy case",
    "Solar power surpasses coal in US electricity generation",
    "Beyoncé adds twenty new tour dates after sellouts",
    "Archaeologists uncover ancient Roman villa in England",
    "GM announces $5 billion investment in EV manufacturing",
    "Flood waters submerge dozens of villages in Bangladesh",
    "New York pizza shop wins international competition",
    "Pentagon confirms successful hypersonic missile test",
    "Average mortgage rate falls below 6% for first time in years",
    "Massive python found in Florida swamp breaks state record",
    "Streaming wars heat up as Disney+ adds password sharing fees",
    "City council approves new affordable housing development",
    "Concert promoter sued over festival cancellation",
    "Gas prices drop ahead of holiday travel weekend",
    "Researchers warn of accelerating Antarctic ice loss",
    "Famous chef opens new restaurant in downtown Chicago",
    "School district adopts AI tools for personalized learning",
    "Train derailment causes chemical spill in Ohio town",
    "Olympic committee announces new host city for 2036 Games",
    "Insurance giant reports massive losses from natural disasters",
    "Hospital ransomware attack disrupts emergency services",
    "Police arrest suspect in cold case murder from 1987",
    "Bitcoin breaks $100,000 barrier in record-setting rally",
    "Endangered rhino gives birth at San Diego Zoo",
    "Local high school robotics team wins national championship",
    "Heatwave breaks temperature records across Europe",
    "James Webb telescope captures images of distant galaxy",
    "Major studio greenlights sequel to summer blockbuster",
    "Dairy farmers warn of milk shortage this winter",
    "Tech CEO testifies before Congress on data privacy",
    "Surgeon performs first successful transplant of pig kidney",
    "Vintage guitar sells at auction for record $4 million",
    "Submarine cable damage disrupts internet across three countries",
    "New variant of COVID detected in wastewater samples",
    "Construction begins on world's tallest residential tower",
    "Documentary about climate activist wins Sundance award",
    "Detroit unveils plans for new downtown sports complex",
    "Whistleblower exposes safety violations at chemical plant",
    "Tennis star wins fourth consecutive Grand Slam title",
    "Bookstore chain files for bankruptcy protection",
    "Volcano eruption in Iceland disrupts air travel",
    "Country music festival announces 2026 lineup",
    "Federal judge blocks new immigration enforcement rule",
    "Researchers find microplastics in human bloodstream",
    "Major car insurance company expands to ten new states",
    "Renowned violinist debuts new symphony in Vienna",
    "Drone delivery service launches in Texas suburbs",
    "Government shutdown averted with last-minute deal",
    "Famous painting stolen from European museum recovered",
    "Energy drink company recalls product over caffeine levels",
    "NBA trade deadline brings blockbuster three-team deal",
    "Astronomers detect strange radio signal from distant star",
    "Mortgage applications surge as rates continue to fall",
    "Wildlife photographer captures rare Amur leopard sighting",
    "Major wildfire in Greece threatens historic monastery",
    "New restaurant opens to two-month waitlist",
    "Stock market hits all-time high amid earnings season",
    "Pediatricians issue new screen time guidelines",
    "Subway expansion project breaks ground in Los Angeles",
    "Vintage Star Wars figure sells for $200,000 at auction",
    "Power grid operator warns of summer blackout risk",
    "MLB pitcher throws perfect game against rivals",
    "AI startup raises $400 million in Series C funding",
    "Public library introduces robot assistants for shelving",
    "Antarctic research station reports unusual penguin migration",
    "Whiskey distillery celebrates 200-year anniversary",
    "Smartphone maker unveils device with three-day battery life",
    "Massive sinkhole swallows car in residential neighborhood",
    "University announces full scholarship program for veterans",
    "Famous bridge closes for major restoration project",
    "Beekeeper rescues swarm from city hall building",
    "New treatment shows promise for early Alzheimer's patients",
    "Music streaming service introduces lossless audio tier",
    "Diamond ring found in donation pile sells for thousands",
]


async def main():
    headlines = [
        {"id": f"h{i:03d}", "headline": text}
        for i, text in enumerate(SAMPLE_HEADLINES, start=1)
    ]

    emojis = await classify_all(headlines)

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    for h in headlines:
        print(f"{emojis[h['id']]}  {h['headline']}")
    print("=" * 80)
    print(f"Total classified: {len(emojis)}/{len(headlines)}")


if __name__ == "__main__":
    asyncio.run(main())
