import pytest

from sebex.analysis.graph import DependentsGraph
from sebex.analysis.model import Language, DependencyUpdate
from sebex.analysis.version import Version, VersionSpec
from sebex.checksum import Checksum
from sebex.config.manifest import ProjectHandle
from sebex.edit.span import Span
from sebex.release.state import ReleaseState, PhaseState, ProjectState, ReleaseStage
from tests.analysis.mock_database import chain_db, triangle_db


def test_petname_deterministic():
    db = chain_db(1)
    assert Checksum.of(db) == Checksum('feccf1c633f39b97d339786c864c9eb079ef4c20')
    assert Checksum.of(db).petname == 'Duly Up Pup'


def test_new_no_release():
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    project = ProjectHandle.parse('a0')
    rel = ReleaseState.plan(
        project=project,
        to_version=db.about(project).version,
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(sources={project: db.about(project).version}, phases=[])


def test_source_already_released():
    db = chain_db(
        versions={'a0': '2.0.0'},
        specs=lambda _pkg, _dep, _vs: VersionSpec.parse('~> 1.0'),
    )
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='a0',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                )
            ]),
        ],
    )


def test_release_stable_patch_without_deps():
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.0.1')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.0.1'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ])
        ],
    )


def test_release_stable_minor_without_deps():
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.1.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.1.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ])
        ],
    )


def test_release_stable_major_without_deps():
    db = chain_db(1)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ])
        ],
    )


def test_release_stable_patch_with_one_level_of_deps():
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.0.1')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.0.1'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
        ],
    )


def test_release_stable_minor_with_one_level_of_deps_with_targeting_spec():
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.1.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.1.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
        ],
    )


def test_release_stable_minor_with_one_level_of_deps_with_higher_spec():
    db = chain_db(
        versions={'a0': '1.2.0'},
        specs=lambda _pkg, _dep, _vs: VersionSpec.parse('~> 1.2'),
    )
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.3.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.3.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.2.0'),
                    to_version=Version.parse('1.3.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
        ],
    )


def test_release_stable_major_with_one_level_of_deps():
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='a0',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                )
            ]),
        ],
    )


def test_release_indirect_bump_with_one_level_of_deps():
    db = chain_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.2.3'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.2.3')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.2.3'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
        ],
    )


def test_release_pre_patch():
    db = chain_db(width=2, versions={'a0': '0.1.0', 'b0': '1.0.0', 'b1': '0.1.0'})
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('0.1.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('0.1.1')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('0.1.0'),
                    to_version=Version.parse('0.1.1'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
        ],
    )


def test_release_pre_minor():
    db = chain_db(width=2, versions={'a0': '0.1.0', 'b0': '1.0.0', 'b1': '0.1.0'})
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('0.2.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('0.2.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('0.1.0'),
                    to_version=Version.parse('0.2.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                )
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='a0',
                            from_spec=VersionSpec.parse('~> 0.1.0'),
                            to_spec=VersionSpec.parse('~> 0.2.0'),
                            to_spec_span=Span.ZERO,
                        )
                    ],
                ),
                ProjectState(
                    project=ProjectHandle.parse('b1'),
                    from_version=Version.parse('0.1.0'),
                    to_version=Version.parse('0.2.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='a0',
                            from_spec=VersionSpec.parse('~> 0.1.0'),
                            to_spec=VersionSpec.parse('~> 0.2.0'),
                            to_spec_span=Span.ZERO,
                        )
                    ],
                ),
            ]),
        ],
    )


def test_triangle():
    db = triangle_db()
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('c'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
        ],
    )


def test_chain_major():
    db = chain_db(height=5)
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('2.0.0'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='a0',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
        ],
    )


def test_current_phase_clean():
    rel = ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
        ],
    )
    assert rel.phases[0].is_clean()
    assert rel.phases[1].is_clean()
    assert rel.current_phase() == rel.phases[0]
    assert rel.is_clean()


def test_current_phase_in_progress_dirty():
    rel = ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    stage=ReleaseStage.PULL_REQUEST_OPENED,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
        ],
    )
    assert rel.phases[0].is_in_progress()
    assert rel.phases[1].is_clean()
    assert rel.current_phase() == rel.phases[0]
    assert rel.is_in_progress()


def test_current_phase_in_progress_clean():
    rel = ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    stage=ReleaseStage.DONE,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
        ],
    )
    assert rel.phases[0].is_done()
    assert rel.phases[1].is_clean()
    assert rel.current_phase() == rel.phases[1]
    assert rel.is_in_progress()


def test_current_phase_done():
    rel = ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    stage=ReleaseStage.DONE,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                    stage=ReleaseStage.DONE,
                ),
            ]),
        ],
    )
    assert rel.phases[0].is_done()
    assert rel.phases[1].is_done()
    assert rel.current_phase() == rel.phases[-1]
    assert rel.is_done()


def test_does_not_release_obsolete_relation():
    db = chain_db(specs=lambda _pkg, _dep, _vs: VersionSpec.parse('~> 0.4.0'))
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.0.1')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.0.1'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
        ],
    )


def test_does_not_release_obsolete_relation_transitive():
    db = chain_db(
        height=3,
        specs=lambda pkg, _dep, vs: (VersionSpec.parse('~> 0.4.0')
                                     if pkg == 'c0' else VersionSpec.targeting(vs[pkg]))
    )
    graph = DependentsGraph.build(db)
    rel = ReleaseState.plan(
        project=ProjectHandle.parse('a0'),
        to_version=Version.parse('1.0.1'),
        db=db,
        graph=graph
    )
    assert rel == ReleaseState(
        sources={ProjectHandle.parse('a0'): Version.parse('1.0.1')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('a0'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.0.1'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                ),
            ]),
        ],
    )


def test_release_stage_ordering():
    vs = [p for p in ReleaseStage]
    assert vs[0] == vs[0]
    assert vs[0] != vs[1]
    assert vs[0] < vs[1]
    assert vs[1] > vs[0]
    assert vs[0].next == vs[1]
    with pytest.raises(StopIteration):
        _ = vs[-1].next
    assert list(iter(vs[0])) == vs[1:]


def test_serialization():
    rel = ReleaseState(
        sources={ProjectHandle.parse('c'): Version.parse('2.0.0')},
        phases=[
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('c'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('2.0.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    stage=ReleaseStage.PULL_REQUEST_OPENED,
                ),
            ]),
            PhaseState([
                ProjectState(
                    project=ProjectHandle.parse('b'),
                    from_version=Version.parse('1.0.0'),
                    to_version=Version.parse('1.1.0'),
                    version_span=Span.ZERO,
                    language=Language.ELIXIR,
                    dependency_updates=[
                        DependencyUpdate(
                            name='c',
                            from_spec=VersionSpec.parse('~> 1.0'),
                            to_spec=VersionSpec.parse('~> 2.0'),
                            to_spec_span=Span.ZERO,
                        ),
                    ],
                ),
            ]),
        ],
    )
    assert ReleaseState(data=rel._make_data()) == rel
