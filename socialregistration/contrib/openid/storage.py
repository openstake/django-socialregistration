import base64
from openid.association import Association
from openid.store.interface import OpenIDStore
from socialregistration.contrib.openid.models import (OpenIDNonce,
    OpenIDStore as OpenIDStoreModel)

class OpenIDStore(OpenIDStore):
    max_nonce_age = 6 * 60 * 60

    def storeAssociation(self, server_url, assoc=None):
        stored_assoc = OpenIDStoreModel.objects.create(
            server_url=server_url,
            handle=assoc.handle,
            secret=base64.encodestring(assoc.secret),
            issued=assoc.issued,
            lifetime=assoc.issued,
            assoc_type=assoc.assoc_type
        )


    def getAssociation(self, server_url, handle=None):
        stored_assocs = OpenIDStoreModel.objects.filter(
            server_url=server_url
        )
        if handle:
            stored_assocs = stored_assocs.filter(handle=handle)

        stored_assocs.order_by('-issued')

        if stored_assocs.count() == 0:
            return None

        return_val = None

        for stored_assoc in stored_assocs:
            assoc = Association(
                stored_assoc.handle, base64.decodestring(stored_assoc.secret),
                stored_assoc.issued, stored_assoc.lifetime, stored_assoc.assoc_type
            )

            if assoc.getExpiresIn() == 0:
                stored_assoc.delete()
            else:
                if return_val is None:
                    return_val = assoc

        return return_val

    def removeAssociation(self, server_url, handle):
        stored_assocs = OpenIDStoreModel.objects.filter(
            server_url=server_url
        )
        if handle:
            stored_assocs = stored_assocs.filter(handle=handle)

        stored_assocs.delete()

    def useNonce(self, server_url, timestamp, salt):
        try:
            nonce = OpenIDNonce.objects.get(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt
            )
        except OpenIDNonce.DoesNotExist:
            nonce = OpenIDNonce.objects.create(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt
            )
            return True

        return False
