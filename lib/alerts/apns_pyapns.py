#
#   Legacy HTTP APNS - requires Python 3+
#
from typing import (
    Any,
    Mapping
)
from pyapns_client import (
    APNSClient,
    IOSPayloadAlert,
    IOSPayload,
    IOSNotification
)
from lib.core.tokens import (
    JsonTKN,
    APNSCFG,
)


def send_apns_alert(
    apns_cfg: Mapping[str, Any],
    alert: Mapping[str, Any],
    device_token: str
) -> bool:
    apns_root: Mapping[str, Any] = apns_cfg[APNSCFG.ROOT.key]
    client = APNSClient(
        mode=APNSClient.MODE_PROD,
        root_cert_path=None,
        auth_key_path=apns_root[APNSCFG.AUTH_KEY_FILEPATH.key],
        auth_key_id=apns_root[APNSCFG.AUTH_KEY_ID.key],
        team_id=apns_root[APNSCFG.TEAM_ID.key]
        )
    body: str = (
        f"{alert[JsonTKN.TICKER.key]} "
        f"{alert[JsonTKN.ALERT_TYPE.key]}: "
        f"{alert[JsonTKN.MESSAGE.key]}"
    )
    alert = IOSPayloadAlert(
        title="StockAlert",
        subtitle="",
        body=body
        )
    payload = IOSPayload(
        alert=alert
        )
    notification = IOSNotification(
        payload=payload,
        topic=apns_root[APNSCFG.TOPIC.key]
        )
    try:
        client.push(
            notification=notification,
            device_token=device_token
        )
        return True
    except Exception:
        return False
    finally:
        client.close()
