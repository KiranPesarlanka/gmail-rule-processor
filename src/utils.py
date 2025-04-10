from dateutil import parser
import pytz

class Utils:

    @staticmethod
    def to_utc(dt_string):
        try:
            # Parse the string to datetime object (with timezone awareness if present)
            dt = parser.parse(dt_string)

            # Convert to UTC
            dt_utc = dt.astimezone(pytz.utc)
            return dt_utc
        except Exception as err:
            print(err)
            return ""

    @staticmethod
    def clean_email_body(text):

        lines = text.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(non_empty_lines)

