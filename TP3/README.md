# APDS TP3: Unsloth Lecture Summary

- **Course:** Advanced Programming for Data Science (APDS)
- **Department:** Applied Mathematics and Statistics (AMS)
- **Lecturer:** Mr.VANN Visal
- **Institution:** Institute of Technology of Cambodia (ITC)
- **Source:** [Unsloth slide V1.pdf](Unsloth%20slide%20V1.pdf)
- **Coverage:** From the beginning through **7. Model & Preprocessor Setup**
  (PDF pages 1–10).

This part of the lesson introduces Unsloth and explains how it helps adapt
pretrained models efficiently. It covers installation, conversation formatting,
fine-tuning benefits, and the decisions needed to select and load a model with
the appropriate input preprocessor.

## 1. Introduction to Unsloth

Unsloth is a Python library for efficient fine-tuning of large language models
(LLMs). The slides mention Llama-3, Mistral, Phi-4, and Gemma as examples of model
families that can be adapted to particular tasks.

A pretrained model already contains knowledge learned during its original
training. Unsloth helps continue that learning with a more focused purpose,
while reducing the computing resources needed for the adaptation.

The lecture emphasizes three goals:

- **Faster training:** reduce the time needed to fine-tune a model.
- **Lower memory usage:** make fine-tuning more practical on limited hardware.
- **Preserving model quality:** improve efficiency while maintaining useful
  results for the intended task.

The slide highlights a memory reduction of around **70%** as an efficiency
benefit. This is a reported benefit in the lecture, rather than a fixed saving
for every model: results depend on the model, hardware, and configuration.

## 2. Installation Requirements

Before installing Unsloth, check that the software environment and available
hardware are suitable for the intended workflow.

| Requirement | Main point from the lesson |
| --- | --- |
| Operating environment | Check platform compatibility. The slide mentions Linux, Windows, macOS, Google Colab, and Kaggle as possible environments. |
| Python | The slide specifies Python 3.9 or later. For an actual installation, choose a version supported by the selected Unsloth release and its dependencies. |
| GPU and memory | Check GPU support and available GPU memory, also called VRAM. The slide highlights NVIDIA CUDA GPUs for faster computation. |
| Package manager | Have `pip` available and keep it updated in the Python environment used for the lesson. |

Compatibility depends on the Unsloth edition and hardware backend. For the
Python-library workflow, consult the
[Unsloth Core requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements#unsloth-core-requirements)
alongside the slide's general checklist. CPU support for some features does not
automatically mean the same fine-tuning workflow can run without a supported
training backend.

## 3. Recommended Installation Method

The lecture recommends installing Unsloth with `pip`. Using `python -m pip`
connects the installation command to the selected Python interpreter:

```bash
python -m pip install --upgrade pip
python -m pip install unsloth
```

After installation, the slide checks that the library can be imported and that
its version can be displayed:

```python
import unsloth

print(unsloth.__version__)
```

If Python reports `ModuleNotFoundError: No module named 'unsloth'`, check that
Unsloth was installed in the same environment as the running script or notebook
kernel. Confirming the interpreter and package location helps identify an
environment mismatch before reinstalling the package.

The [official installation guide](https://unsloth.ai/docs/get-started/install)
provides installation options for the chosen environment.

## 4. Customizable Chat Templates

A chat template defines how a conversation is represented as input to a model.
It marks who is speaking and where messages begin and end, allowing the model to
interpret the conversation structure consistently.

The Llama-3 example in the lecture uses three roles:

- **System:** instructions that guide the assistant's behavior, represented by
  the `{SYSTEM}` placeholder.
- **User:** the question or request, represented by `{INPUT}`.
- **Assistant:** the response, represented by `{OUTPUT}`.

The special tokens shown in the slide serve different purposes:

| Token | Purpose |
| --- | --- |
| `<\|begin_of_text\|>` | Marks the beginning of the input sequence. |
| `<\|start_header_id\|>` and `<\|end_header_id\|>` | Surround the role label, such as `user` or `assistant`. |
| `<\|eot_id\|>` | Marks the end of a conversation turn. |

The slide's simplified structure is:

```text
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{SYSTEM}<|eot_id|><|start_header_id|>user<|end_header_id|>

{INPUT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{OUTPUT}<|eot_id|>
```

The placeholders stand for message content; the special tokens identify the
structure around that content. Different models can expect different formats,
so practical code should use the selected model's matching chat template.
[Hugging Face's chat-template guide](https://huggingface.co/docs/transformers/chat_templating)
explains how model-specific templates preserve that structure.

## 5. Benefits

The lecture describes three benefits of adapting a pretrained model:

1. **Task-specific adaptation:** specialize the model for the vocabulary,
   instructions, or examples relevant to a particular task.
2. **Resource efficiency:** reduce the memory and computation needed for the
   adaptation.
3. **More relevant results:** help the model produce responses that better fit
   the intended use, with quality depending on the examples and training setup.

### Efficient Adaptation with LoRA

The code image on this slide uses `FastVisionModel.get_peft_model(...)` to
configure a vision model for parameter-efficient fine-tuning. **LoRA**, or
Low-Rank Adaptation, learns small adapter updates while keeping the original
model weights frozen. This reduces the number of parameters that need training.

The example selects which parts of the model receive adaptation:

| Setting in the slide | Role |
| --- | --- |
| `finetune_vision_layers=True` | Enables adaptation in the vision component. |
| `finetune_language_layers=True` | Enables adaptation in the language component. |
| `finetune_attention_modules=True` | Includes attention modules, which model relationships between input elements. |
| `finetune_mlp_modules=True` | Includes feed-forward, or MLP, modules that transform internal representations. |

All four options are enabled in the example. Its main LoRA settings are:

| Parameter | Value | Meaning |
| --- | --- | --- |
| `r` | `16` | The adapter rank, which controls adaptation capacity and affects memory use. A larger rank can also increase overfitting risk. |
| `lora_alpha` | `16` | Scales the contribution of the learned adapter updates. |
| `use_rslora` | `False` | Leaves the rank-stabilized LoRA variant disabled. |
| `lora_dropout` | `0` | Applies no LoRA dropout in this configuration. |
| `bias` | `"none"` | Does not train bias parameters through this adapter configuration. |
| `random_state` | `3407` | Sets a random seed to help make experiments reproducible. |
| `loftq_config` | `None` | Leaves the optional LoftQ initialization unconfigured. |

This call prepares the model's adaptation settings; it does not itself run the
training process. The configuration is also illustrated in Unsloth's
[vision fine-tuning guide](https://unsloth.ai/docs/basics/vision-fine-tuning).

## 6. Fine-Tuning

Fine-tuning means continuing the training of a pretrained model on a smaller,
task-specific dataset. It reuses the model's existing knowledge and adjusts its
behavior toward a more focused task.

The diagram in the slide describes this progression:

1. **Initial learning:** a model learns general patterns from a large corpus.
2. **Task adaptation:** the pretrained model is trained further using examples
   relevant to a specific purpose.
3. **Adapted model:** the resulting model is used for the intended application.

For example, a model could be adapted to follow a particular instruction style
using suitable examples. With LoRA, the learned changes are represented by
adapter parameters instead of updating every original model weight.

Fine-tuning changes trainable parameters. **Inference** uses an already loaded
model to produce a response, without performing those training updates.

## 7. Model & Preprocessor Setup

### 7.1 Choosing a Model

The model-selection diagram lists five considerations:

| Consideration | What to evaluate |
| --- | --- |
| Task requirements | Identify the expected inputs and outputs, including whether the task uses text, images, or both. |
| Model size | Balance the model's capacity with memory requirements and processing time. |
| Pretrained vs. fine-tuned | Decide whether to start from a general base model or one already adapted to instructions or a related task. |
| Resource constraints | Check available hardware, VRAM, and time before selecting a model that must fit the environment. |
| Data privacy | Consider where data will be processed and stored, and whether the chosen environment provides the required privacy controls. |

These factors should be considered together. A suitable model fits both the
task and the resources available for working with it.

### 7.2 Understanding the Model Loader

A **model loader** loads a pretrained model's architecture and weights into
memory so the model can be used for inference or further fine-tuning.

- The **architecture** describes the model's structure and layers.
- The **weights** are the learned numerical parameters produced during training.
- Loading makes that structure and learned state available to the program.

Choosing a model and loading it are related but separate decisions: selection
identifies the appropriate checkpoint, while the loader makes it usable in the
chosen environment.

### 7.3 Role of the Preprocessor

To clarify the preprocessor part of this topic, a model needs inputs converted
into the representation it expects:

- For text, a **tokenizer** converts text into token IDs and related inputs.
- For a vision-language model, a **processor** can combine text tokenization with
  image preprocessing.
- The **chat template** supplies the conversation structure expected by a chat
  model before the formatted messages are processed.

Load a tokenizer or processor that matches the selected model checkpoint. A
matching input format ensures the model receives the kinds of tokens and image
representations it was designed to use. The
[Transformers processor documentation](https://huggingface.co/docs/transformers/main_classes/processors)
explains how multimodal processors combine these input-processing components.

## References

- Mr.VANN Visal, [Unsloth slide V1.pdf](Unsloth%20slide%20V1.pdf), Chapter-02,
  PDF pages 1–10.
- Unsloth documentation: [Requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements), [Installation](https://unsloth.ai/docs/get-started/install), and [Vision Fine-tuning](https://unsloth.ai/docs/basics/vision-fine-tuning).
- Hugging Face Transformers documentation: [Chat Templates](https://huggingface.co/docs/transformers/chat_templating) and [Processors](https://huggingface.co/docs/transformers/main_classes/processors).
