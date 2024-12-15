from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from typing import Any, List, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from huggingface_hub import InferenceClient
import os

class LLM(BaseChatModel):

    client: InferenceClient

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override the _generate method to implement the chat model logic.

        This can be a call to an API, a call to a local model, or any other
        implementation that generates a response to the input prompt.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """
        chat_history = kwargs.get("chat_history", [{"role": "system", "content": "You are a friendly assistant"}])
        max_tokens = kwargs.get("max_tokens", 1024)

        for message in messages:
            if isinstance(message, HumanMessage):
                chat_history.append({ "role": "user", "content": message.content })
            elif isinstance(message, AIMessage):
                chat_history.append({ "role": "assistant", "content": message.content })
        
        result = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct", 
            messages=chat_history, 
            temperature=0.1,
            max_tokens=max_tokens,
            top_p=0.7,
            stream=False
        )

        message = AIMessage(content=result.choices[0].message.content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "llama"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "llama-3.2-instruct-3b"
        }
    
if __name__ == "__main__":
    client = InferenceClient(api_key=os.environ["HF_TOKEN"])
    custom_llm = LLM(client=client)

    result = custom_llm.invoke([HumanMessage(content="Xin chào")], chat_history=[{"role": "system", "content": "You are a friendly assistant2"}])
    print(result.content)