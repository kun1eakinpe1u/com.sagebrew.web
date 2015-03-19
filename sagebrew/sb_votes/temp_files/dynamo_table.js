[
    {
        "table_name": "users_full",
        "hash_key": "username"
    },
    {
        "table_name": "comments",
        "hash_key": "parent_object",
        "range_key": "datetime"
    },
    {
        "table_name": "votes",
        "hash_key": "parent_object",
        "range_key": "user",
        "local_index_name": "VoteStatusIndex",
        "local_index": "status",
        "type": "N"
    },
    {
        "table_name": "users_barebones",
        "hash_key": "username"
    },
    {
        "table_name": "friends",
        "hash_key": "username"
    },
    {
        "table_name": "private_questions",
        "hash_key": "object_uuid"
    },
    {
        "table_name": "private_solutions",
        "hash_key": "parent_object",
        "range_key": "object_uuid"
    },
    {
        "table_name": "public_questions",
        "hash_key": "object_uuid"
    },
    {
        "table_name": "public_solutions",
        "hash_key": "parent_object",
        "range_key": "object_uuid"
    },
    {
        "table_name": "posts",
        "hash_key": "parent_object",
        "range_key": "datetime"
    },
    {
        "table_name": "news_feed",
        "hash_key": "username"
    },
    {
        "table_name": "flags",
        "hash_key": "parent_object",
        "range_key": "user",
        "local_index_name": "FlagTypeIndex",
        "local_index": "flag_type",
        "type": "S"
    },
    {
        "table_name": "notifications",
        "hash_key": "username"
    },
    {
        "table_name": "location",
        "hash_key": "state",
        "range_key": "district"
    },
    {
        "table_name": "house_reps",
        "hash_key": "username",
        "range_key": "state",
        "local_index_name": "DistrictIndex",
        "local_index": "district",
        "type": "N"
    },
    {
        "table_name": "senators",
        "hash_key": "username",
        "range_key": "state"
    },
    {
        "table_name": "edits",
        "hash_key": "parent_object",
        "range_key": "datetime",
        "local_index_name": "UserIndex",
        "local_index": "user",
        "type": "S"
    },
    {
        "table_name": "vote_versions",
        "hash_key": "parent_object",
        "range_key": "time",
        "local_index_name": "UserIndex",
        "local_index": "user",
        "type": "S"
    }]