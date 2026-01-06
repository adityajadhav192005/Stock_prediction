from rest_framework import serializers

class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)
    mode = serializers.ChoiceField(
        choices=(('live', 'live'), ('cached', 'cached'), ('demo', 'demo')),
        required=False,
        default='live',
    )
