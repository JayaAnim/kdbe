from django import forms


class VerificationVerify(forms.Form):
    key = forms.CharField(label="Verification Code")
    
    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean(self):
        super().clean()
        
        if self.errors:
            return None

        # Check if the key can be verified
        try:
            self.instance.verify(self.cleaned_data["key"])
        except self.instance.IncorrectKey:
            self.add_error("key", "The auth code entered was incorrect")
        except self.instance.VerificationExpired:
            self.add_error("key", "This verification code is no longer valid")

    def save(self, *args, **kwargs):
        return self.instance
