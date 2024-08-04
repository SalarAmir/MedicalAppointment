import requests

server_url = 'https://googlecloudapi.vercel.app/api/v1'

def get_annotations(image):
    response = requests.post(f'{server_url}/image/annotations', files={'file': image})
    return response.json()

if __name__ == "__main__":
    response = get_annotations(open('page.png', 'rb'))
    print(response["data"].keys())

    texts = response["data"]["textAnnotations"]
    print("Texts:")

    for text in texts:
        print(f'\n"{text["description"]}"')

        vertices = [
            f"({vertex['x']},{vertex['y']})" for vertex in text["boundingPoly"]["vertices"]
        ]

        print("bounds: {}".format(",".join(vertices)))
