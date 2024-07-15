from anthropic import Anthropic

class QueryAnthropic():
    def __init__(self, anthropic_api_key) -> None:
    
        self.__anthropic_api_key = anthropic_api_key

    def query_claude(self, search_string, model):
        
        client = Anthropic(
            # This is the default and can be omitted
            api_key=self.__anthropic_api_key,
        )

        message = client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": search_string,
                }
            ],
            model = model
        )
        
        return message.content