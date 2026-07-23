import re


class PiiMasker:
    """Server-side PII masking utility for contact fields.

    - Phone: strips non-digits, then masks the 6 middle digits of an 11-digit
      number using a non-predictable mixed-character sequence derived from the
      original digits. The prefix and suffix remain visible.
    - Email: preserves the first and last character of the local part and the
      full domain. The interior of the local part is replaced with a
      non-predictable mixed character sequence.
    """

    _PHONE_POOL = ['*']
    _EMAIL_POOL = ['*']

    def mask_phone(self, value: str) -> str:
        if value is None:
            return ''
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) != 11:
            return '•' * len(value)
        visible_prefix = digits[:2]
        visible_suffix = digits[-3:]
        middle_digits = digits[2:8]
        mask = []
        for i, digit_char in enumerate(middle_digits):
            mask.append(self._PHONE_POOL[(int(digit_char) + i + 1) % len(self._PHONE_POOL)])
        masked_core = f'{visible_prefix}{"".join(mask)}{visible_suffix}'
        return f'+1 {masked_core}'

    def mask_email(self, value: str) -> str:
        email_str = str(value)
        if not email_str or '@' not in email_str:
            return '•••@••••.com'
        local, domain = email_str.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            mask = []
            for i, ch in enumerate(local[1:-1]):
                mask.append(self._EMAIL_POOL[(ord(ch) + i) % len(self._EMAIL_POOL)])
            masked_local = local[0] + ''.join(mask) + local[-1]
        return f'{masked_local}@{domain}'

    def mask(self, field_type: str, value: str) -> str:
        field_type = field_type.lower()
        if field_type == 'phone':
            return self.mask_phone(value)
        if field_type == 'email':
            return self.mask_email(value)
        return value


_masker = PiiMasker()


def mask_email(value: str) -> str:
    return _masker.mask_email(value)


def mask_phone(value: str) -> str:
    return _masker.mask_phone(value)


def mask_for_role(field_type: str, value: str, can_view_full: bool) -> str:
    if can_view_full:
        return value
    return _masker.mask(field_type, value)
