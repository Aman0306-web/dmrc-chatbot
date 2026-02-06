from dmrc_assistant import DMRCAssistant

if __name__ == '__main__':
    assistant = DMRCAssistant()
    q = "How to recharge metro card?"
    result = assistant.process_query(q, "en")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
