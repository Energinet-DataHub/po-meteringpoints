from typing import List, Optional
from dataclasses import dataclass, field

from energytt_platform.api import Endpoint, Context
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import MeteringPointQuery
from meteringpoints_shared.models import \
    MeteringPointFilters, MeteringPointOrdering


class GetGsrnList(Endpoint):
    """
    Returns a list of available GSRN numbers.
    """

    @dataclass
    class Response:
        gsrn: List[str]

    @db.session()
    def handle_request(
            self,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        # query = MeteringPointQuery(session) \
        #     .is_accessible_by(context.token.subject) \
        #     .get_distinct_gsrn()
        gsrn = MeteringPointQuery(session) \
            .get_distinct_gsrn()

        return self.Response(
            gsrn=gsrn,
        )


class GetMeteringPointList(Endpoint):
    """
    Looks up many Measurements, optionally filtered and ordered.
    """

    @dataclass
    class Request:
        offset: int
        limit: int
        filters: Optional[MeteringPointFilters] = field(default=None)
        ordering: Optional[MeteringPointOrdering] = field(default=None)

    @dataclass
    class Response:
        total: int
        meteringpoints: List[MeteringPoint]

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        # query = MeteringPointQuery(session) \
        #     .is_accessible_by(context.token.subject)
        query = MeteringPointQuery(session)

        if request.filters:
            query = query.apply_filters(request.filters)

        results = query \
            .offset(request.offset) \
            .limit(request.limit)

        if request.ordering:
            results = results.apply_ordering(request.ordering)

        return self.Response(
            total=query.count(),
            meteringpoints=results.all(),
        )


class GetMeteringPointDetails(Endpoint):
    """
    Returns details about a single MeteringPoint.
    """

    @dataclass
    class Request:
        gsrn: str

    @dataclass
    class Response:
        success: bool
        meteringpoint: Optional[MeteringPoint]

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        # meteringpoint = MeteringPointQuery(session) \
        #     .is_accessible_by(context.token.subject) \
        #     .has_gsrn(request.gsrn) \
        #     .one_or_none()
        meteringpoint = MeteringPointQuery(session) \
            .has_gsrn(request.gsrn) \
            .one_or_none()

        return self.Response(
            success=meteringpoint is not None,
            meteringpoint=meteringpoint,
        )
