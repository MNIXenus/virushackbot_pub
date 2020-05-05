from programy.clients.events.console.client import ConsoleBotClient
import programy.clients.args as args
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Args(args.ClientArguments):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.args = None
        self._bot_root = os.path.join(BASE_DIR, "storage")
        config_dir = os.path.join(BASE_DIR, "config")
        platform = "xnix" if os.name == "posix" else "windows"
        self._logging = os.path.join(config_dir, platform, "logging.yaml")
        self._config_name = os.path.join(config_dir, platform, "config.yaml")
        self._config_format = 'yaml'
        self._no_loop = False
        self._substitutions = None

    def parse_args(self, client):
        pass

class BotClientMod(ConsoleBotClient):
    def __init__(self):
        super().__init__()
        self.clients = {}

    def parse_arguments(self, *args, **kwargs):
        client_args = Args()
        client_args.parse_args(self)
        return client_args

    def get_context(self, uid):
        if uid not in self.clients:
            self.clients[uid] = self.create_client_context(uid)
        return(self.clients[uid])

    def get_answer(self, uid, text):
        context = self.get_context(uid)
        answer = self.clients[uid].bot.ask_question(context, text, responselogger=self)
        return(answer)

    def get_topic(self, uid):
        context = self.get_context(uid)
        conversation = context.bot.get_conversation(context)
        topic = conversation.property("topic")
        return(topic)

    def get_var(self, uid, var):
        context = self.get_context(uid)
        conversation = context.bot.get_conversation(context)
        topic = conversation.property(var)
        return(topic)

    def get_rdf(self, uid, subj, pred, obj):
        context = self.get_context(uid)
        rdf_arr = context.brain.rdf.matched_as_tuples(subj, pred, obj)
        return(rdf_arr)

    def set_var(self, uid, var, value):
        context = self.get_context(uid)
        conversation = context.bot.get_conversation(context)
        conversation.properties[var] = value
