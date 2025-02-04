from typing import List

from config import IMAGE_URL_API_URL
from logger import logger
from models import ImageUrlInfo, ImageUrlInfosRequestData, ImageUrlInfosResponse
from services.module import ApiClient

TEST_MODE = True
MOCK_IMAGE_URL_INFOS = {
    'persona': '책을 좋아하는 사람',
    'image_infos': [
        {
            'keyword': '책',
            'image_url': 'https://search.pstatic.net/sunny/?src=https%3A%2F%2Fpng.pngtree.com%2Fpng-clipart%2F20240723%2Foriginal%2Fpngtree-open-book-with-fluttering-pages-png-image_15615914.png&type=a340'
        },
        {
            'keyword': '바다 풍경',
            'image_url': 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2F20150615_260%2Fkiu4941_1434373285217XGAeQ_JPEG%2F150615_215281.jpg&type=sc960_832'
        },
        {
            'keyword': '북한산',
            'image_url': 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDA5MTlfMTkz%2FMDAxNzI2NzM5NDcwNjEy.ANq33BOilmDQ5jr2CY2p6zJFL3DGMbDp_4NHwd0GPqUg.gyi1TonqZJrP-mJH1u69FRyMZ6p_6SYIqzNiVM8sQegg.JPEG%2F1000006686.jpg&type=sc960_832'
        },
        {
            'keyword': '제주도',
            'image_url': 'https://search.pstatic.net/common/?src=http%3A%2F%2Fpost.phinf.naver.net%2FMjAyNDA1MjVfMTk3%2FMDAxNzE2NjAyODA2MTE1.JxstfT4FRzKuphvoceLoivByOQcb1tEcb72X2UCaPtYg.UawIphGrKDuJAOUiGDncGlHuudfA_QdlxWRFzqjjaewg.PNG%2FI1qFI446cuRhri-mgiylRRV_hNFI.jpg&type=sc960_832'
        },
        {
            'keyword': '자기개발 도서',
            'image_url': 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzEyMTdfMTYg%2FMDAxNzAyNzkxMzEwMzI2.T4b67cOy80WEZa4CBjOxeqYw9GddmAcI-jaZ1PB7R_4g.Xd3uEzjSaTSXvPnNZsz1lPPr05VIb1aXX3xtlq3wufgg.JPEG.swr0211%2Foutput_1695693303.jpg&type=sc960_832'
        },
        {
            'keyword': '북 카페',
            'image_url': 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzAyMDJfMjgw%2FMDAxNjc1MzQwNDY0NTYz.9AsIkzM2hvyii_eCA-M-V6-ylrpMdTIEzwQpNorV-aQg.fuNAS4hZIObCi-eNxZXoCou-3H1y6DYztbjpUgQsb1Ug.JPEG.jin30330%2Fbook_cafe5.jpg&type=sc960_832'
        }
    ],
}


def request_image_url_infos(username: str) -> ImageUrlInfosResponse:
    logger.info(f"{username.rjust(12)}| request_questions")

    if TEST_MODE:
        json_response = MOCK_IMAGE_URL_INFOS

    else:
        api_client = ApiClient()

        req_data = ImageUrlInfosRequestData(username=username)
        json_response = api_client.post(IMAGE_URL_API_URL, data=req_data.dict())

    return ImageUrlInfosResponse(**json_response)


def get_image_url_infos(username) -> List[ImageUrlInfo]:
    response = request_image_url_infos(username)
    return response.image_infos
