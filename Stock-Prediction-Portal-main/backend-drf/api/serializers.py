from rest_framework import serializers

class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)
    mode = serializers.ChoiceField(choices=(('live','live'), ('demo','demo')), required=False, default='live')