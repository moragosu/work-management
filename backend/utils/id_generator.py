import uuid
import data_store

COUNTER_FILE = "id_counters.json"


def next_counter_id(prefix: str, existing_items: list = None) -> str:
    """카운터 기반 순차 ID 생성. 삭제해도 카운터는 내려가지 않음."""
    counters = data_store.load(COUNTER_FILE)
    if prefix not in counters:
        max_num = 0
        if existing_items:
            for item in existing_items:
                try:
                    num = int(item["id"].replace(prefix, ""))
                    if num > max_num:
                        max_num = num
                except (ValueError, KeyError):
                    pass
        counters[prefix] = max_num
    next_num = counters[prefix] + 1
    counters[prefix] = next_num
    data_store.save(COUNTER_FILE, counters)
    return f"{prefix}{next_num}"


def get_reusable_ids(items: list, prefix: str) -> list:
    """카운터 범위 내에서 현재 존재하지 않는 (재사용 가능한) ID 목록 반환."""
    counters = data_store.load(COUNTER_FILE)
    max_counter = counters.get(prefix, 0)
    if max_counter <= 0:
        return []
    existing_nums = set()
    for item in items:
        try:
            num = int(item["id"].replace(prefix, ""))
            existing_nums.add(num)
        except (ValueError, KeyError):
            pass
    return [f"{prefix}{n}" for n in range(1, max_counter + 1) if n not in existing_nums]


def get_next_id_preview(prefix: str, existing_items: list = None) -> str:
    """카운터를 증가시키지 않고 다음 ID만 미리보기."""
    counters = data_store.load(COUNTER_FILE)
    if prefix not in counters:
        max_num = 0
        if existing_items:
            for item in existing_items:
                try:
                    num = int(item["id"].replace(prefix, ""))
                    if num > max_num:
                        max_num = num
                except (ValueError, KeyError):
                    pass
        return f"{prefix}{max_num + 1}"
    return f"{prefix}{counters[prefix] + 1}"


def sync_counter(prefix: str, used_id: str, existing_items: list):
    """사용자가 직접 입력한 ID가 카운터보다 크면 카운터를 해당 값으로 갱신."""
    try:
        num = int(used_id.replace(prefix, ""))
    except ValueError:
        return
    counters = data_store.load(COUNTER_FILE)
    if prefix not in counters:
        max_num = 0
        for item in existing_items:
            try:
                n = int(item["id"].replace(prefix, ""))
                if n > max_num:
                    max_num = n
            except (ValueError, KeyError):
                pass
        counters[prefix] = max_num
    if num > counters[prefix]:
        counters[prefix] = num
    data_store.save(COUNTER_FILE, counters)


def short_uuid(prefix: str) -> str:
    """짧은 랜덤 ID 생성 (예: 'S3F2A1B4')."""
    return f"{prefix}{str(uuid.uuid4())[:8].upper()}"
