from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from typing import Any, List, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from huggingface_hub import InferenceClient

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
        chat_history = [
            { "role": "system", "content": "Bạn là một trợ lý ảo. Nếu người dùng hỏi những câu liên quan đến bất động sản, tìm nhà, hãy trả lời \"[CALL_TOOL]\". Còn lại thì trả lời như bình thường" },
            { "role": "user", "content": "Xin chào" },
            { "role": "assistant", "content": "Xin chào! Rất vui được gặp bạn. Tôi có thể giúp gì cho bạn hôm nay?" },
            { "role": "user", "content": "Tìm nhà ở Hà Nội" },
            { "role": "assistant", "content": "[CALL_TOOL]" },
            { "role": "user", "content": "Bạn là ai" },
            { "role": "assistant", "content": "Xin chào! Tôi là trợ lý ảo của bạn, được tạo ra để hỗ trợ bạn trong nhiều vấn đề khác nhau. Tôi có thể giúp bạn tìm thông tin, giải đáp thắc mắc, và nhiều hơn thế. Bạn cần tôi giúp gì hôm nay?" },
            { "role": "user", "content": "Cho tôi thông tin về chung cư mini ở Hồ Chí Minh" },
            { "role": "assistant", "content": "[CALL_TOOL]" }
        ]

        for message in messages:
            if isinstance(message, HumanMessage):
                chat_history.append({ "role": "user", "content": message.content })
            elif isinstance(message, AIMessage):
                chat_history.append({ "role": "assistant", "content": message.content })
        
        result = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct", 
            messages=chat_history, 
            temperature=0.1,
            max_tokens=1024,
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
    client = InferenceClient(api_key="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")
    custom_llm = LLM(client=client)

    result = custom_llm.invoke([HumanMessage(content="Xin chào")])
    print(result.content)