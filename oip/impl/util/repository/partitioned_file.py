import os
from typing import TypeVar, List, Optional

from oip.base.util.repository import Repository
from oip.base.util.serialization import Serializer, Deserializer
from oip.impl.util.repository.key_extraction import KeyExtractor
from oip.impl.util.util import next_prime, stable_hash

T = TypeVar('T')


class PartitionedFileRepository(Repository[T]):
    def __init__(self,
                 file_path: str,
                 serializer: Serializer[T],
                 deserializer: Deserializer[T],
                 key_extractor: KeyExtractor[T],
                 min_partitions: int = 1,
                 max_partitions: Optional[int] = None,
                 max_partition_size: int = 32 * 1024,
                 partition_size_factor: float = 1.0,
                 rebalance_threshold: float = 1.0):
        self._serializer = serializer
        self._deserializer = deserializer
        self._key_extractor = key_extractor

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        self._file_name = file_name
        self._file_ext = file_ext

        self._dir_path = os.path.join(os.path.dirname(file_path), file_name)
        os.makedirs(self._dir_path, exist_ok=True)

        self._partitions_count = self._get_initial_partitions_count()
        self._min_partitions = max(min_partitions, 1)
        self._max_partitions = max(max_partitions, 1) if max_partitions else None
        self._max_partition_size = max(max_partition_size, 1024)
        self._partition_size_factor = max(partition_size_factor, 1.0)
        self._rebalance_threshold = max(rebalance_threshold, 1.0)

        if self._need_rebalance():
            self._rebalance()

    def load(self, key: str) -> Optional[T]:
        file_path = self.get_file_path_by_key(key)

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as file:
            for line in file:
                serialized_obj = line.strip()
                if not serialized_obj:
                    continue
                obj = self._deserializer.deserialize(serialized_obj)
                obj_key = self._key_extractor.extract_key(obj)
                if obj_key == key:
                    return obj

        return None

    def save(self, obj: T):
        self.save_all([obj])

    def load_all(self) -> List[T]:
        objs = list[T]()

        for file_name in os.listdir(self._dir_path):
            partition_file_path = os.path.join(self._dir_path, file_name)
            objs += self._load_all_from_partition(partition_file_path)

        return sorted(list(set(objs)))

    def save_all(self, objs: List[T]):
        self._save_all(objs, update=True)

        if self._need_rebalance():
            self._rebalance()

    def get_file_path_by_key(self, key: str) -> str:
        key_hash = stable_hash(key)
        obj_partition = key_hash % self._partitions_count
        file_name = f"{self._file_name}_{obj_partition}{self._file_ext}"
        file_path = os.path.join(self._dir_path, file_name)
        return file_path

    def _load_all_from_partition(self, partition_file_path: str) -> list[T]:
        if not os.path.exists(partition_file_path):
            return list[T]()

        objs = list[T]()

        with open(partition_file_path, 'r') as file:
            for line in file:
                serialized_obj = line.strip()
                if not serialized_obj:
                    continue
                obj = self._deserializer.deserialize(serialized_obj)
                objs.append(obj)

        return objs

    def _save_all(self, objs: List[T], update: bool = True):
        objs_partitions = dict[str, list[T]]()

        for obj in objs:
            key = self._key_extractor.extract_key(obj)
            partition_file_path = self.get_file_path_by_key(key)
            if not objs_partitions.get(partition_file_path):
                objs_partitions[partition_file_path] = list[T]()
            objs_partitions[partition_file_path].append(obj)

        for partition_file_path, partition_objs in objs_partitions.items():
            self._save_all_to_partition(partition_file_path, partition_objs, update)

    def _save_all_to_partition(self, partition_file_path: str, objs: List[T], update: bool = True):
        saved_objs = list[T]()
        if update:
            saved_objs = self._load_all_from_partition(partition_file_path)

        objs_to_save = {self._key_extractor.extract_key(obj): obj for obj in saved_objs}

        for obj in objs:
            key = self._key_extractor.extract_key(obj)
            objs_to_save[key] = obj

        with open(partition_file_path, 'w') as file:
            for obj in sorted(objs_to_save.values()):
                serialized_obj = self._serializer.serialize(obj)
                if not serialized_obj:
                    continue
                file.write(serialized_obj + '\n')

    def _need_rebalance(self) -> bool:
        if self._partitions_count < self._min_partitions:
            return True

        if self._max_partitions and self._partitions_count >= self._max_partitions:
            return False

        partition_size_cost = 0.0
        for file_name in os.listdir(self._dir_path):
            partition_file_path = os.path.join(self._dir_path, file_name)
            partition_size_cost += os.path.getsize(partition_file_path)
        partition_size_cost *= self._partition_size_factor
        partition_size_cost /= self._max_partition_size

        total_cost = partition_size_cost
        normalized_total_cost = total_cost / self._partitions_count

        return normalized_total_cost > self._rebalance_threshold

    def _rebalance(self):
        objs = self.load_all()
        self._partitions_count = self._get_next_partitions_count()
        self._save_all(objs, update=False)

    def _get_initial_partitions_count(self) -> int:
        return len(os.listdir(self._dir_path))

    def _get_next_partitions_count(self):
        return next_prime(self._partitions_count)
