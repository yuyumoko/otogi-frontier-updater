import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ujson as json
import unittest

from core.OtogiFrontier import OtogiApi

proxy = ""
access_token = "8df2b195-bf29-42b5-9d4e-ab6da6614f55"
access_token = ""

test_character_id = 21491
test_char_episodes = json.loads(
    '{"RootMonsterId":21491,"RootSpiritId":0,"Favorite":false,"Episodes":[{"MSceneAdultFlowId":5957,"Title":"\\u672a\\u6765\\u306f\\u5f7c\\u5973\\u306e\\u76ee\\u306e\\u4e2d","MSceneId":221491,"UseRichScene":true,"MAdultId":221491,"IsBinaural":false,"Viewable":true,"Viewed":false,"EpisodeUnlockType":0,"Description":" \\u9032\\u5316\\u6bb5\\u968e2\\u3067\\u89e3\\u653e","Rewards":[{"ItemType":8,"ItemId":0,"Quantity":5}]},{"MSceneAdultFlowId":5958,"Title":"\\u9032\\u5316\\u7279\\u5178","MSceneId":null,"UseRichScene":false,"MAdultId":null,"IsBinaural":false,"Viewable":true,"Viewed":false,"EpisodeUnlockType":0,"Description":" \\u9032\\u5316\\u6bb5\\u968e3\\u3067\\u89e3\\u653e","Rewards":[{"ItemType":6,"ItemId":312132,"Quantity":1},{"ItemType":8,"ItemId":0,"Quantity":5}]},{"MSceneAdultFlowId":5959,"Title":"\\u30cf\\u30fc\\u30c9\\u30e9\\u30c3\\u30af\\u3092\\u4e57\\u308a\\u8d8a\\u3048\\u308d","MSceneId":221492,"UseRichScene":true,"MAdultId":221492,"IsBinaural":true,"Viewable":true,"Viewed":false,"EpisodeUnlockType":0,"Description":" \\u9032\\u5316\\u6bb5\\u968e4\\u3067\\u89e3\\u653e","Rewards":[{"ItemType":8,"ItemId":0,"Quantity":5}]},{"MSceneAdultFlowId":5960,"Title":"\\u8ee2\\u3070\\u306c\\u5148\\u306b","MSceneId":221493,"UseRichScene":true,"MAdultId":null,"IsBinaural":false,"Viewable":false,"Viewed":false,"EpisodeUnlockType":0,"Description":" \\u9032\\u5316\\u6bb5\\u968e5\\u3067\\u89e3\\u653e","Rewards":[{"ItemType":5,"ItemId":30002,"Quantity":1},{"ItemType":8,"ItemId":0,"Quantity":5}]}]}'
)


class TestOtogiApi(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = OtogiApi(access_token, proxy)

    @unittest.skip("need access token")
    async def test_getUserCharacterIDS(self):
        character_ids = await self.api.char.getUserCharacterIDS()
        self.assertIsNotNone(character_ids)
        self.assertGreater(len(character_ids), 0)

    @unittest.skip("need access token")
    async def test_getCharacterInfo(self):
        charInfo = await self.api.char.getCharacterInfo(test_character_id)
        self.assertIsNotNone(charInfo)
        self.assertEqual(charInfo["id"], test_character_id)

    @unittest.skip("need access token")
    async def test_getCharacterEpisodes(self):
        char_episodes = await self.api.char.getCharacterEpisodes(test_character_id)
        self.assertIsNotNone(char_episodes)
        self.assertEqual(char_episodes["RootMonsterId"], test_character_id)

    @unittest.skip("1")
    async def test_getMScenes(self):
        MScenes = await self.api.char.getMScenes(
            test_char_episodes["Episodes"][0]["MSceneId"]
        )
        self.assertIsNotNone(MScenes)
        self.assertNotEqual(len(MScenes), 0)

    @unittest.skip("1")
    async def test_getCharacterStand(self):
        CharaStand_data = await self.api.resource.getCharacterStand(test_character_id)
        self.assertIsNotNone(CharaStand_data)
        self.assertTrue(CharaStand_data.startswith(b"UnityFS"))


if __name__ == "__main__":
    unittest.main()
