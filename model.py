from typing import List

import pandas as pd
from pydantic import BaseModel


class ImageInfo(BaseModel):
    search_word: str
    image_url: str


class ImageQuestions(BaseModel):
    image_infos: List[ImageInfo]
    questions: List[str]

    @property
    def image_df(self) -> pd.DataFrame:
        df = pd.DataFrame([info.model_dump() for info in self.image_infos])
        df["image_preview"] = df["image_url"]
        df = df[["image_preview", "search_word", "image_url"]]

        return df
