from matcher.object_pair import ObjectPair


class ObjectPairer:

    def create_pairs(self, old_lookup, new_lookup):

        pairs = []

        matched_new_ids = set()

        # First pass
        # Create Matched and Removed pairs

        for object_id, old_object in old_lookup.items():

            if object_id in new_lookup:

                pair = ObjectPair(
                    old_object,
                    new_lookup[object_id]
                )

                matched_new_ids.add(object_id)

            else:

                pair = ObjectPair(
                    old_object,
                    None
                )

            pairs.append(pair)

        # Second pass
        # Create Added pairs

        for object_id, new_object in new_lookup.items():

            if object_id not in matched_new_ids:

                pair = ObjectPair(
                    None,
                    new_object
                )

                pairs.append(pair)

        return pairs