defmodule Sebex.ElixirAnalyzer do
  alias Sebex.ElixirAnalyzer.AnalysisReport
  alias Sebex.ElixirAnalyzer.Span

  @spec analyze_mix_exs_file!(path :: Path.t()) :: AnalysisReport.t() | no_return
  def analyze_mix_exs_file!(path) do
    analyze_mix_exs_source!(File.read!(path))
  end

  @spec analyze_mix_exs_source!(source :: String.t()) :: AnalysisReport.t() | no_return
  def analyze_mix_exs_source!(source) do
    ast = parse!(source)

    {version, version_span} =
      case extract_version_attr(ast) do
        nil -> raise {:error, :version_attr_not_found}
        x -> x
      end

    dependencies = extract_dependencies(ast)

    %AnalysisReport{version: version, version_span: version_span, dependencies: dependencies}
  end

  @spec parse!(source :: String.t()) :: Macro.t() | no_return
  defp parse!(source) do
    Code.string_to_quoted!(source,
      columns: true,
      token_metadata: true,
      literal_encoder: &encode_literal/2
    )
  end

  defp encode_literal(lit, meta) do
    {:ok, {:literal, meta, [lit]}}
  end

  @spec decode_literal(Macro.t()) :: term
  defp decode_literal(ast) do
    Macro.prewalk(ast, fn
      {:literal, _, [lit]} -> lit
      node -> node
    end)
  end

  @spec extract_version_attr(Macro.t()) :: {String.t(), Span.t()} | nil
  defp extract_version_attr(ast) do
    {_, result} =
      Bunch.Macro.prewalk_while(ast, nil, fn
        t, {_, _} = acc ->
          {:skip, t, acc}

        {:@, _, [{:version, _, [{:literal, _, [token]} = literal]}]} = t, _
        when is_binary(token) ->
          {:skip, t, {token, Span.literal(literal)}}

        t, acc ->
          {:enter, t, acc}
      end)

    result
  end

  @spec extract_dependencies(Macro.t()) :: list(AnalysisReport.Dependency.t())
  defp extract_dependencies(ast) do
    ast |> extract_deps_list() |> Enum.map(&process_dep/1)
  end

  @spec extract_deps_list(Macro.t()) :: list(Macro.t())
  defp extract_deps_list(ast) do
    {_, result} =
      Bunch.Macro.prewalk_while(ast, :not_found, fn
        t, {:found, _} = acc ->
          {:skip, t, acc}

        {kw_def, _,
         [
           {:deps, _, nil},
           [
             {
               {:literal, _, [:do]},
               {:literal, _, [deps_list]}
             }
           ]
         ]} = t,
        :not_found
        when kw_def in [:def, :defp] and is_list(deps_list) ->
          {:skip, t, {:found, deps_list}}

        t, :not_found ->
          {:enter, t, :not_found}
      end)

    case result do
      {:found, l} -> l
      :not_found -> []
    end
  end

  @spec process_dep(Macro.t()) :: AnalysisReport.Dependency.t()
  defp process_dep(
         {:literal, _,
          [
            {
              {:literal, _, [name]},
              {:literal, _, [version_spec]} = version_literal
            }
          ]}
       )
       when is_atom(name) and is_binary(version_spec) do
    %AnalysisReport.Dependency{
      name: name,
      version_spec: version_spec,
      version_spec_span: Span.literal(version_literal)
    }
  end

  defp process_dep(
         {:{}, _,
          [
            {:literal, _, [name]},
            {:literal, _, [version_spec]} = version_literal,
            _
          ]}
       )
       when is_atom(name) and is_binary(version_spec) do
    %AnalysisReport.Dependency{
      name: name,
      version_spec: version_spec,
      version_spec_span: Span.literal(version_literal)
    }
  end

  defp process_dep(
         {:literal, tuple_meta,
          [
            {
              {:literal, _, [name]},
              [{first_key, _} | _] = kw
            }
          ]}
       )
       when is_atom(name) do
    %AnalysisReport.Dependency{
      name: name,
      version_spec: kw |> decode_literal() |> Enum.into(%{}),
      version_spec_span:
        Span.literal(first_key) |> Span.set(Keyword.fetch!(tuple_meta, :closing), :end)
    }
  end
end