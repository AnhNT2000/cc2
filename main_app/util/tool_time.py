from datetime import datetime, timedelta

# Function to convert string time to timedelta
def convert_to_timedelta(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)

def get_max_time(time_ranges):
    max_span = timedelta()
    most_comprehensive_range = None

    # Calculate the span of each range
    for start_time, end_time in time_ranges:
        start = convert_to_timedelta(start_time)
        end = convert_to_timedelta(end_time)

        # Adjust the end time if it's before the start time (considering it's a next day)
        if end < start:
            end += timedelta(days=1)

        span = end - start

        if span > max_span:
            max_span = span
            most_comprehensive_range = (start_time, end_time)

    return most_comprehensive_range

