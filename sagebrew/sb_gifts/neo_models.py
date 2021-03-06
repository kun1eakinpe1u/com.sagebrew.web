from neomodel import (db, RelationshipTo, StringProperty, BooleanProperty)

from api.neo_models import SBObject


class Giftlist(SBObject):
    """
    Giftlists are lists of Products which users can purchase for a Mission.
    They are a list of items available on Amazon and found via the
    Amazon Product API.
    """
    # Whether or not the list is currently able to be viewed by the public or
    # if it is still being edited
    public = BooleanProperty(default=False)

    # Which Mission has this list of gifts they want from their supporters
    mission = RelationshipTo("sb_missions.neo_models.Mission", "LIST_FOR")

    def get_product(self, vendor_id, vendor_name):
        query = 'MATCH (g:Giftlist {object_uuid:"%s"})<-[:IN_LIST]-' \
                '(p:Product {vendor_id:"%s", vendor_name:"%s"}) RETURN p' \
                % (self.object_uuid, vendor_id, vendor_name)
        res, _ = db.cypher_query(query)
        if res.one:
            res.one.pull()
            return Product.inflate(res.one)
        return None

    def get_products(self):
        query = 'MATCH (g:Giftlist {object_uuid:"%s"})<-[:IN_LIST]-' \
                '(p:Product) RETURN p' % self.object_uuid
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Product.inflate(row[0]) for row in res]

    def get_product_vendor_ids(self):
        query = 'MATCH (g:Giftlist {object_uuid:"%s"})<-[:IN_LIST]-' \
                '(p:Product) RETURN p.vendor_id' % self.object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    def get_mission(self):
        from sb_missions.neo_models import Mission
        query = 'MATCH (g:Giftlist {object_uuid:"%s"})-[:LIST_FOR]->' \
                '(m:Mission) RETURN m' % self.object_uuid
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return Mission.inflate(res.one)


class Product(SBObject):
    """
    Products are items which are found via the Amazon Product API and
    are used to represent an item available on Amazon in a
    Giftlist owned by Missions.
    """
    # Can use ItemLookup from Amazon to get more information such as price,
    # availability, etc. using the vendor_id
    # Initially we only utilize the Amazon Product API so we can only lookup
    # via ASIN (Amazon Search Identification Number)
    # which is set as vendor_id here
    vendor_id = StringProperty()
    # Initially we only utilize Amazon Product Search so we set
    # amazon by default
    # In the future we can utilize many more product search engines
    # and allow for more in depth look ups across multiple services
    vendor_name = StringProperty(default="amazon")

    # Whether or not this item has been purchased for the Mission
    # Not currently use as nothing is ever removed from the front-facing
    # mission Giftlist unless the Mission owner removes it from the list
    # purchased = BooleanProperty(default=False)

    # relationships
    # Which list this product is in
    giftlist = RelationshipTo("sb_gifts.neo_models.Giftlist", "IN_LIST")
    # Which orders this product is included in
    orders = RelationshipTo("sb_orders.neo_models.Order", "INCLUDED_IN")

    def get_giftlist(self):
        query = 'MATCH (p:Product {object_uuid:"%s"})-[:IN_LIST]->' \
                '(g:Giftlist) RETURN g' % (self.object_uuid)
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return Giftlist.inflate(res.one)
