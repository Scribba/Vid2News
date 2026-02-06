import requests


class FacebookPublisher:
    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token

    def publish(self, content) -> bool:
        payload = {
            "message": content,
            "access_token": self.access_token
        }
        url = f"https://graph.facebook.com/v24.0/{self.page_id}/feed"
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            post_id = response.json().get("id")
            print(f"Post successfully published: {post_id}")
            return True
        else:
            print(f"Failed to upload post: {response.status_code}")
            print(response.text)
            return False