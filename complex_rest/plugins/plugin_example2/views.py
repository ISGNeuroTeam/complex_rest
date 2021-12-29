import json
import datetime
import pandas as pd
import numpy as np

from rest.response import Response
from rest.decorators import api_view, permission_classes
from rest import permissions


@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def hello(request):
    return Response({'msg': 'Hello plugin_example2'})


@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def random_dataframe(request):
    dates = pd.date_range(datetime.datetime.now(), periods=6)
    df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))

    return Response(
        json.loads(
            df.to_json(orient="split")
        )
    )



