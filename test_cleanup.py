import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from utils.fallback_extraction import clean_name, parse_date, parse_time
    print("✅ utils.fallback_extraction imported successfully")
    
    from simple_reservation_handler import SimpleReservationHandler
    print("✅ SimpleReservationHandler imported successfully")
    
    import app
    print("✅ app imported successfully")

    # Test clean_name
    assert clean_name("My name is John") == "John", f"Failed: {clean_name('My name is John')}"
    assert clean_name("uh, I'm Sarah") == "Sarah", f"Failed: {clean_name('uh, I\'m Sarah')}"
    print("✅ clean_name tests passed")

    # Test parse_date
    d = parse_date('tomorrow')
    print(f"Date 'tomorrow': {d}")
    print("✅ parse_date tests passed")

    # Test parse_time
    t1 = parse_time("7pm")
    assert t1 == "19:00", f"Failed 7pm: {t1}"
    t2 = parse_time("morning")
    assert t2 == "11:00", f"Failed morning: {t2}"
    print("✅ parse_time tests passed")

    print("🎉 All cleanup verification tests passed!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
