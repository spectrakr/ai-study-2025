pdf_setting = {
    "aliases": {},
    "mappings": {
        "properties": {
            "metadata": {
                "properties": {
                    "CreationDate": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "Creator": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "ModDate": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "Producer": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "file_path": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "page": {"type": "long"},
                    "source": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "total_pages": {"type": "long"},
                }
            },
            "text": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                "analyzer": "custom_nori_analyzer",
            },
            "timestamp": {"type": "date"},
            "value": {"type": "keyword"},
            "vector": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine",
                "index_options": {
                    "type": "int8_hnsw",
                    "m": 16,
                    "ef_construction": 100,
                },
            },
        }
    },
    "settings": {
        "index": {
            "routing": {
                "allocation": {"include": {"_tier_preference": "data_content"}}
            },
            "number_of_shards": "1",
            "analysis": {
                "filter": {
                    "nori_filter": {
                        "type": "nori_part_of_speech",
                        "stoptags": [],
                    }
                },
                "analyzer": {
                    "custom_nori_analyzer": {
                        "filter": ["nori_filter", "lowercase"],
                        "tokenizer": "custom_nori_tokenizer",
                    }
                },
                "tokenizer": {"custom_nori_tokenizer": {"type": "nori_tokenizer"}},
            },
        }
    },
}
