import petname
import pytest

from analysis.mock_database import chain_db, triangle_db
from sebex.analysis import DependentsGraph, Version
from sebex.config import ProjectHandle
from sebex.release import ReleaseState, PhaseState, ProjectReleaseState


@pytest.fixture
def mock_codename(monkeypatch):
    monkeypatch.setattr(petname, 'generate', lambda _, sep: f'code{sep}name')


def test_new_no_release(mock_codename):
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    project = ProjectHandle.parse('a0')
    rel = ReleaseState.new(
        project=project,
        to_version=db.about(project).version,
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([])


def test_release_stable_patch_without_deps(mock_codename):
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.0.1'),
            )
        ])
    ])


def test_release_stable_minor_without_deps(mock_codename):
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.1.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            )
        ])
    ])


def test_release_stable_major_without_deps(mock_codename):
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('2.0.0'),
            )
        ])
    ])


def test_release_stable_patch_with_one_level_of_deps(mock_codename):
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.0.1'),
            )
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.0.1'),
            )
        ]),
    ])


def test_release_stable_minor_with_one_level_of_deps(mock_codename):
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.1.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            )
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.0.1'),
            )
        ]),
    ])


def test_release_stable_major_with_one_level_of_deps(mock_codename):
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('2.0.0'),
            )
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            )
        ]),
    ])


def test_release_pre_patch(mock_codename):
    db = chain_db(width=2, versions={'a0': '0.1.0', 'b0': '1.0.0', 'b1': '0.1.0'})
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('0.1.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('0.1.0'),
                to_version=Version.parse('0.1.1'),
            )
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.0.1'),
            ),
            ProjectReleaseState(
                project=ProjectHandle.parse('b1'),
                from_version=Version.parse('0.1.0'),
                to_version=Version.parse('0.1.1'),
            ),
        ]),
    ])


def test_release_pre_minor(mock_codename):
    db = chain_db(width=2, versions={'a0': '0.1.0', 'b0': '1.0.0', 'b1': '0.1.0'})
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('0.2.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a0'),
                from_version=Version.parse('0.1.0'),
                to_version=Version.parse('0.1.1'),
            )
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b0'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            ),
            ProjectReleaseState(
                project=ProjectHandle.parse('b1'),
                from_version=Version.parse('0.1.0'),
                to_version=Version.parse('0.2.0'),
            ),
        ]),
    ])


def test_transitive_dep(mock_codename):
    db = triangle_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.new(
        project=ProjectHandle.parse('c'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState([
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('c'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('2.0.0'),
            ),
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('b'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            ),
        ]),
        PhaseState([
            ProjectReleaseState(
                project=ProjectHandle.parse('a'),
                from_version=Version.parse('1.0.0'),
                to_version=Version.parse('1.1.0'),
            ),
        ]),
    ])