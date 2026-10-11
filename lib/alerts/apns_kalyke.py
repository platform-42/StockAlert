#
#   Modern HTTP/2 APNS - requires Python 3.9+
#
from typing import (
    Any,
    Mapping,
    Coroutine,
)

import asyncio
import kalyke

from lib.core.tokens import (
    JsonTKN,
    APNSCFG,
)


def _run_async(
    coro: Coroutine[Any, Any, None]
) -> None:
    try:
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
    else:
        loop.create_task(coro)


def send_apns_alert(
    apns_cfg: Mapping[str, Any],
    alert: Mapping[str, Any],
    device_token: str
) -> None:
    apns_root: Mapping[str, Any] = apns_cfg[APNSCFG.ROOT.key]
    client: kalyke.ApnsClient = kalyke.ApnsClient(
        use_sandbox=apns_root[APNSCFG.SANDBOX.key],
        team_id=apns_root[APNSCFG.TEAM_ID.key],
        auth_key_id=apns_root[APNSCFG.AUTH_KEY_ID.key],
        auth_key_filepath=apns_root[APNSCFG.AUTH_KEY_FILEPATH.key],
    )

    body: str = (
        f"{alert[JsonTKN.TICKER.key]} "
        f"{alert[JsonTKN.ALERT_TYPE.key]}: "
        f"{alert[JsonTKN.MESSAGE.key]}"
    )

    payload: kalyke.Payload = kalyke.Payload(
        alert=kalyke.PayloadAlert(
            title="StockAlert",
            body=body,
        ),
        badge=1,
        sound="default",
    )

    config: kalyke.ApnsConfig = kalyke.ApnsConfig(
        topic=apns_root[APNSCFG.TOPIC.key]
    )

    try:
        send_coro: Coroutine[Any, Any, None] = client.send_message(
            device_token=device_token,
            payload=payload,
            apns_config=config,
        )
        _run_async(send_coro)
    except Exception as exc:
        # Log, don't crash monitoring
        print(f"APNS send failed: {exc}")
