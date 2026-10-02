import json
import logging
import os
from typing import Any, Optional

import requests
from pydantic import BaseModel


class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _normalize_body(body: Any) -> Optional[Any]:
        if body is None:
            return None

        if isinstance(body, BaseModel):
            return body.model_dump(mode="json", by_alias=True, exclude_none=True)

        if isinstance(body, list) and body and isinstance(body[0], BaseModel):
            return [item.model_dump(mode="json", by_alias=True, exclude_none=True) for item in body]

        # dict, list[dict], прочее — оставляем как есть
        return body

    def send_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[dict] = None,
        expected_status: int = 200,
        need_logging: bool = True,
        **kwargs,
    ):
        url = f"{self.base_url}{endpoint}"
        payload = self._normalize_body(data)

        response = self.session.request(
            method, url, json=payload, params=params, **kwargs
        )

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise ValueError(
                f"Unexpected status code: {response.status_code}. "
                f"Expected: {expected_status}"
            )
        return response

    def update_session_headers(self, headers: dict):
        self.session.headers.update(headers)

    def log_request_and_response(self, response):
        try:
            request = response.request
            GREEN, RED, RESET = "\033[32m", "\033[31m", "\033[0m"
            full_test_name = (
                f"pytest "
                f"{os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"
            )
            headers = " \\\n".join(
                [f"-H '{h}: {v}'" for h, v in request.headers.items()]
            )
            body = ""
            if getattr(request, "body", None):
                body = (
                    request.body.decode("utf-8")
                    if isinstance(request.body, bytes)
                    else request.body
                )
                body = f"-d '{body}' \n" if body and body != "{}" else ""

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n{body}"
            )

            response_data = response.text
            try:
                response_data = json.dumps(
                    json.loads(response.text), indent=4, ensure_ascii=False
                )
            except json.JSONDecodeError:
                pass

            color = GREEN if response.ok else RED
            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            self.logger.info(
                f"\tSTATUS_CODE: {color}{response.status_code}{RESET}\n"
                f"\tDATA:\n{color}{response_data}{RESET}"
            )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"Logging failed: {type(e)} - {e}")