from langchain_openai import ChatOpenAI
import Config

print("# -> PROVIDERS INSTALLED ")
Providers = list(Config.OpenAI_API_Providers.keys())
for Provider in Providers:
    print(f"# {Providers.index(Provider)} -> {Provider}")
print("#-------------------------------------------------#")
print("# -> BASIC MODEL (INFORMATION)"); Choise = -1
while int(Choise) not in range(0, len(Providers)):
    Choise = input("# -> Введите номер провайдера API: ")
Model = input(f"# -> Введите название модели ({Config.OpenAI_API_Providers[Providers[int(Choise)]]['model']}):")
if Model == "": Model = Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"]
Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"] = Model
AI_Basic = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
print("#-------------------------------------------------#")
print("# -> FUNCTIONAL MODEL (OUTPUT)"); Choise = -1
while int(Choise) not in range(0, len(Providers)):
    Choise = input("# -> Введите номер провайдера API: ")
Model = input(f"# -> Введите название модели ({Config.OpenAI_API_Providers[Providers[int(Choise)]]['model']}):")
if Model == "": Model = Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"]
Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"] = Model
AI_Function = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
print("#-------------------------------------------------#")