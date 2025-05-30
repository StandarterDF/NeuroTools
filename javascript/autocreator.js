CurrentModel_Info = ""
CurrentModel_Func = ""
CurrentProvider_Info = ""
CurrentProvider_Func = ""

async function GenerateButton() {
    /*
    Topic: str
    TopicCount: str
    SubTopicGen: bool 
    ThinkMode: bool 
    GenPDF: bool
    ModelInfo: str
    ModelFunc:str
    ModelInfoProvider:str
    ModelFuncProvider:str 
    */
    var Theme = document.getElementById("var_project_theme").value;
    var ThemeCount = document.getElementById("var_project_theme_count").value;
    var SubGeneration = document.getElementById("var_subchart_generation").checked;
    var PDFGeneration = document.getElementById("var_pdf_generation").checked;
    var Thinking = document.getElementById("var_thinking").checked;
    var ThinkingOutput = document.getElementById("var_thinking_output").checked;
    var RequestData = {
        "Topic": Theme,
        "TopicCount": ThemeCount,
        "SubTopicGen": SubGeneration,
        "ThinkMode": Thinking,
        "GenPDF": PDFGeneration,
        "ModelInfo": CurrentModel_Info,
        "ModelFunc": CurrentModel_Func,
        "ModelInfoProvider": CurrentProvider_Info,
        "ModelFuncProvider": CurrentProvider_Func
    }
    var State = await fetch("http://127.0.0.1:22222/autocreator_getstate");
    StateText = await State.text();
    if (StateText == "None")
    {
        URL_Result = await fetch("http://127.0.0.1:22222/autocreator_generate", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(RequestData)
        });
    }
    else if (StateText == "Complete") {
        var Filename = await fetch("http://127.0.0.1:22222/autocreator_getfile");
        window.open('http://127.0.0.1:22222/Docs/' + await Filename.text(), '_blank');
    }
    else 
    {
        var State = await fetch("http://127.0.0.1:22222/autocreator_getstate");
        if (StateText == "WaitForCommand")
        {
            var RequestData = {
                "CMD": "regenerate"
            }
            await fetch("http://127.0.0.1:22222/autocreator_command", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8'
                },
                body: JSON.stringify(RequestData)
            });
        }
    }
    console.log(RequestData);
}

async function SkipButton()
{
    var State = await fetch("http://127.0.0.1:22222/autocreator_getstate");
    if (await State.text() == "WaitForCommand")
    {
        var RequestData = {
            "CMD": "continue"
        }
        await fetch("http://127.0.0.1:22222/autocreator_command", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(RequestData)
        });
    }
}

document.getElementById("GenerateButton").onclick = GenerateButton;
document.getElementById("SkipButton").onclick = SkipButton;

for (var element of document.getElementsByClassName("ProviderButton")) {
    element.onclick = function () {
        for (var elem1 of document.getElementsByClassName("ProviderSelector"))
        {
            if (elem1.getAttribute("modetype") == this.getAttribute("modetype") && elem1.getAttribute("provider") == this.getAttribute("provider"))
            {
                elem1.classList.remove("d-none");
                if (this.getAttribute("modetype") == "Инф. модель")
                {
                    CurrentModel_Info = elem1.value;
                    console.log("# CHANGED INFO: " + String(CurrentModel_Info));
                }
                else if (this.getAttribute("modetype") == "Функ. модель")
                {
                    CurrentModel_Func = elem1.value;
                    console.log("# CHANGED FUNC: " + String(CurrentModel_Func));
                }
            }
            else
            {
                if (elem1.getAttribute("modetype") == this.getAttribute("modetype")) {
                    elem1.classList.add("d-none");
                }
            }
        }
    }
}

for (var elem1 of document.getElementsByClassName("ProviderSelector")) {
    if (elem1.getAttribute("modetype") == "Инф. модель")
    {
        if (!elem1.classList.contains("d-none")) { CurrentModel_Info = elem1.value; CurrentProvider_Info = elem1.getAttribute("provider"); }
    }
    if (elem1.getAttribute("modetype") == "Функ. модель")
    {
        if (!elem1.classList.contains("d-none")) { CurrentModel_Func = elem1.value; CurrentProvider_Func = elem1.getAttribute("provider"); }
    }
}

for (var elem1 of document.getElementsByClassName("ProviderSelector")) {
    elem1.addEventListener("change", function () {
        if (this.getAttribute("modetype") == "Инф. модель")
        {
            CurrentModel_Info = this.value;
            CurrentProvider_Info = this.getAttribute("provider");
            console.log("# CHANGED INFO: " + String(CurrentModel_Info) + " " + String(CurrentProvider_Info));
        }
        else if (this.getAttribute("modetype") == "Функ. модель")
        {
            CurrentModel_Func = this.value;
            CurrentProvider_Func = this.getAttribute("provider");
            console.log("# CHANGED FUNC: " + String(CurrentModel_Func) + " " + String(CurrentProvider_Func));
        }
    });
}

setInterval(async function () {
    var Logs = (await fetch("http://127.0.0.1:22222/autocreator_log"));
    document.getElementById("TextGeneration_LOGS").value = await Logs.text();
    console.log(Logs);
}, 500);

console.log("# INFO: " + String(CurrentModel_Info));
console.log("# FUNC: " + String(CurrentModel_Func));