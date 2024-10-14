from model import ImageQuestions, ImageInfo


def _tmp_get_image_questions(img_num: int) -> ImageQuestions:
    if img_num == 1:
        return ImageQuestions(
            image_infos=[
                ImageInfo(
                    image_url="https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDA4MDNfMjIz%2FMDAxNzIyNjc3MDEwMTUy.dyg43ieNTiE5fzg5AiwkAIzptIqTH9kEsNKHMASdcscg.ivFm-0Pybpvhu_D-BqpQvo6MgOehgv75hBonY6cY7yQg.JPEG%2FDALL%25A1%25A4E_2024-08-03_18.23.04_-_A_high-quality_image_of_a_pile_of_fresh_potatoe.jpg&type=a340",
                    search_word="potato"
                )
            ],
            questions=[
                "What is in the image?",
                "How many potatoes are there?",
                "What color are the potatoes?",
                "What is the shape of the potatoes?",
            ]
        )

    elif img_num == 2:
        return ImageQuestions(
            image_infos=[
                ImageInfo(
                    image_url="https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDA4MDNfMjIz%2FMDAxNzIyNjc3MDEwMTUy.dyg43ieNTiE5fzg5AiwkAIzptIqTH9kEsNKHMASdcscg.ivFm-0Pybpvhu_D-BqpQvo6MgOehgv75hBonY6cY7yQg.JPEG%2FDALL%25A1%25A4E_2024-08-03_18.23.04_-_A_high-quality_image_of_a_pile_of_fresh_potatoe.jpg&type=a340",
                    search_word="potato"
                ),
                ImageInfo(
                    image_url="https://search.pstatic.net/sunny/?src=https%3A%2F%2Fcdn.pixabay.com%2Fphoto%2F2017%2F05%2F24%2F11%2F46%2Fhorse-2340340_1280.jpg&type=a340",
                    search_word="horse"
                )
            ],
            questions=[
                "What is in the image?",
                "How many horses are there?",
                "What color is the horse?",
                "What is the horse doing?",
            ]
        )

    elif img_num == 3:
        return ImageQuestions(
            image_infos=[
                ImageInfo(
                    image_url="https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDA4MDNfMjIz%2FMDAxNzIyNjc3MDEwMTUy.dyg43ieNTiE5fzg5AiwkAIzptIqTH9kEsNKHMASdcscg.ivFm-0Pybpvhu_D-BqpQvo6MgOehgv75hBonY6cY7yQg.JPEG%2FDALL%25A1%25A4E_2024-08-03_18.23.04_-_A_high-quality_image_of_a_pile_of_fresh_potatoe.jpg&type=a340",
                    search_word="potato"
                ),
                ImageInfo(
                    image_url="https://search.pstatic.net/sunny/?src=https%3A%2F%2Fcdn.pixabay.com%2Fphoto%2F2017%2F05%2F24%2F11%2F46%2Fhorse-2340340_1280.jpg&type=a340",
                    search_word="horse"
                ),
                ImageInfo(
                    image_url="https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDAxMTZfMTA0%2FMDAxNzA1MzgyMTYzODQy.aOfdhRwL111ZWGhlsHq2PjCk4xzcwfAKQIiyvZC5x9sg.hfU8T1uepjAbyz_pDlF3-mtGazhk-wzqyjhBNE5rd9Ag.PNG.skan220522%2F20240116_140220.png&type=sc960_832",
                    search_word="초가집"
                )
            ],
            questions=[
                "What is in the image?",
                "How many potatoes are there?",
                "What color is the horse?",
                "What is the horse doing?",
                "What is the shape of the house?",
            ]
        )