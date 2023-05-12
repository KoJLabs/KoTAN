from transformers import NllbTokenizer, AutoModelForSeq2SeqLM
import torch
from tqdm import tqdm
from transformers import BatchEncoding

class KoNTATranslationFactory():
    """
    Machine translation using NLLN Meta model

    - dataset: Train
    - metric: BLEU score
        +-----------------+-----------------+------------+
        | Source Language | Target Language | BLEU score |
        +=================+=================+============+
        | English         |  Korean         |            |
        +-----------------+-----------------+------------+
        | Korean          |  English        |            |
        +-----------------+-----------------+------------+

    Args:
        src (str): source language
        
    Returns:
        str: machine translation Class

    Examples:
        >>> mt = KoNTA(task="translation", tgt="en")
    """
    def __init__(
            self,
            task: str,
            src: str,
            LANG_ALIASES: dict
            ):
        super().__init__()
        self.task = task
        self.src = src
        self.LANG_ALIASES = LANG_ALIASES

    def load(self, device: str):
        tokenizer = NllbTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", src_lang=self.src)
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M").to(device)

        return KoNTATranslation(
            model,
            tokenizer,
            device,
            self.LANG_ALIASES
        )
    

class KoNTATranslation:
    def __init__(self, model, tokenizer, device, LANG_ALIASES) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.LANG_ALIASES = LANG_ALIASES

    def predict(self, text, tgt):
        """
        Predict a translation result

        Args:
            text (str): input text
            tgt (str): target language

        Returns:
            output (str): A translation result
        """
        
        inputs = self.tokenizer(text, return_tensor="pt")

        if isinstance(inputs['input_ids'], list):
            input_dict = {}            
            input_dict['input_ids'] = torch.LongTensor(inputs['input_ids']).reshape(1,len(inputs['input_ids']))
            input_dict['attention_mask'] = torch.LongTensor(inputs['attention_mask']).reshape(1,len(inputs['attention_mask']))
            inputs = BatchEncoding(input_dict)
            
        translated_tokens = self.model.generate(
            **inputs.to(self.device), forced_bos_token_id=self.tokenizer.lang_code_to_id[self.LANG_ALIASES[tgt]], max_length=128
        )

        output = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
            
        return output
    

