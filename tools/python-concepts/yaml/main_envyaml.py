from envyaml import EnvYAML

# read file env.yaml and parse config
env = EnvYAML("config.yaml")

print(env["local"]["database"])
print(env["prod"]["database"])
