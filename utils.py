def clean_node_names(x: str) -> str:
    return str.replace(x, '_', ' ').capitalize().replace('-', 'START').upper()
