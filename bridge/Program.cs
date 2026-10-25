using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.Script.Serialization;
using GameRes;

namespace GarexBridge
{
    class Program
    {
        private static JavaScriptSerializer m_serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };

        static void Main(string[] args)
        {
            Console.OutputEncoding = new UTF8Encoding(false);
            Console.InputEncoding = new UTF8Encoding(false);

            InitGameData();

            string line;
            while ((line = Console.ReadLine()) != null)
            {
                line = line.Trim();
                if (string.IsNullOrEmpty(line))
                    continue;

                Dictionary<string, object> req = null;
                string id = "";
                try
                {
                    req = m_serializer.Deserialize<Dictionary<string, object>>(line);
                    if (req != null && req.ContainsKey("id"))
                        id = req["id"] != null ? req["id"].ToString() : "";
                }
                catch (Exception ex)
                {
                    WriteError("", "INVALID_JSON", "Failed to parse JSON request: " + ex.Message);
                    continue;
                }

                string cmd = req.ContainsKey("cmd") && req["cmd"] != null ? req["cmd"].ToString() : "";
                Dictionary<string, object> cmdArgs = req.ContainsKey("args") && req["args"] is Dictionary<string, object>
                    ? (Dictionary<string, object>)req["args"]
                    : new Dictionary<string, object>();

                try
                {
                    HandleCommand(id, cmd, cmdArgs);
                }
                catch (Exception ex)
                {
                    WriteError(id, "COMMAND_FAILED", ex.Message);
                }
            }
        }

        static void InitGameData()
        {
            try
            {
                string schemeFile = Path.Combine(FormatCatalog.Instance.DataDirectory, "Formats.dat");
                if (File.Exists(schemeFile))
                {
                    using (var stream = File.OpenRead(schemeFile))
                    {
                        FormatCatalog.Instance.DeserializeScheme(stream);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[garex-bridge] Scheme init warning: " + ex.Message);
            }
        }

        static void HandleCommand(string id, string cmd, Dictionary<string, object> args)
        {
            switch (cmd.ToLowerInvariant())
            {
                case "ping":
                    WriteSuccess(id, new Dictionary<string, object> { { "pong", true }, { "version", "1.0.0" } });
                    break;

                case "quit":
                case "exit":
                    WriteSuccess(id, new Dictionary<string, object> { { "bye", true } });
                    Environment.Exit(0);
                    break;

                case "formats":
                    HandleFormats(id);
                    break;

                case "probe":
                    HandleProbe(id, args);
                    break;

                case "list":
                    HandleList(id, args);
                    break;

                case "extract":
                    HandleExtract(id, args);
                    break;

                case "convert_image":
                    HandleConvertImage(id, args);
                    break;

                case "convert_audio":
                    HandleConvertAudio(id, args);
                    break;

                default:
                    WriteError(id, "UNKNOWN_COMMAND", "Unrecognized command: " + cmd);
                    break;
            }
        }

        static void HandleFormats(string id)
        {
            var catalog = FormatCatalog.Instance;
            var list = new List<Dictionary<string, object>>();

            foreach (var arc in catalog.ArcFormats)
            {
                list.Add(FormatToDict(arc, "archive", arc.CanWrite));
            }
            foreach (var img in catalog.ImageFormats)
            {
                list.Add(FormatToDict(img, "image", img.CanWrite));
            }
            foreach (var aud in catalog.AudioFormats)
            {
                list.Add(FormatToDict(aud, "audio", aud.CanWrite));
            }
            foreach (var scr in catalog.ScriptFormats)
            {
                list.Add(FormatToDict(scr, "script", scr.CanWrite));
            }

            WriteSuccess(id, new Dictionary<string, object>
            {
                { "total", list.Count },
                { "formats", list }
            });
        }

        static Dictionary<string, object> FormatToDict(IResource res, string kind, bool canCreate)
        {
            return new Dictionary<string, object>
            {
                { "tag", res.Tag },
                { "kind", kind },
                { "description", res.Description },
                { "extensions", res.Extensions != null ? res.Extensions.ToArray() : new string[0] },
                { "can_create", canCreate }
            };
        }

        static void HandleProbe(string id, Dictionary<string, object> args)
        {
            if (!args.ContainsKey("path") || args["path"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'path'");
                return;
            }

            string path = args["path"].ToString();
            if (!File.Exists(path))
            {
                WriteError(id, "FILE_NOT_FOUND", "File not found: " + path);
                return;
            }

            try
            {
                using (var arc = ArcFile.TryOpen(path))
                {
                    if (arc != null)
                    {
                        WriteSuccess(id, new Dictionary<string, object>
                        {
                            { "recognized", true },
                            { "kind", "archive" },
                            { "format", arc.Tag },
                            { "description", arc.Description }
                        });
                        return;
                    }
                }

                WriteSuccess(id, new Dictionary<string, object>
                {
                    { "recognized", false }
                });
            }
            catch (Exception ex)
            {
                WriteError(id, "PROBE_FAILED", ex.Message);
            }
        }

        static void HandleList(string id, Dictionary<string, object> args)
        {
            if (!args.ContainsKey("path") || args["path"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'path'");
                return;
            }

            string path = args["path"].ToString();
            if (!File.Exists(path))
            {
                WriteError(id, "FILE_NOT_FOUND", "File not found: " + path);
                return;
            }

            try
            {
                using (var arc = ArcFile.TryOpen(path))
                {
                    if (arc == null)
                    {
                        WriteError(id, "UNSUPPORTED_FORMAT", "File format is not recognized as a supported archive: " + path);
                        return;
                    }

                    var entries = new List<Dictionary<string, object>>();
                    foreach (var entry in arc.Dir)
                    {
                        long size = entry.Size;
                        object packedSize = null;

                        var packed = entry as PackedEntry;
                        if (packed != null && packed.IsPacked)
                        {
                            size = packed.UnpackedSize;
                            packedSize = (long)entry.Size;
                        }

                        entries.Add(new Dictionary<string, object>
                        {
                            { "name", entry.Name },
                            { "size", size },
                            { "packed_size", packedSize },
                            { "offset", entry.Offset },
                            { "type", entry.Type ?? "" }
                        });
                    }

                    WriteSuccess(id, new Dictionary<string, object>
                    {
                        { "format", arc.Tag },
                        { "description", arc.Description },
                        { "count", entries.Count },
                        { "entries", entries }
                    });
                }
            }
            catch (Exception ex)
            {
                WriteError(id, "OPEN_FAILED", ex.Message);
            }
        }

        static void HandleExtract(string id, Dictionary<string, object> args)
        {
            if (!args.ContainsKey("path") || args["path"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'path'");
                return;
            }
            if (!args.ContainsKey("destination") || args["destination"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'destination'");
                return;
            }

            string path = args["path"].ToString();
            if (!File.Exists(path))
            {
                WriteError(id, "FILE_NOT_FOUND", "File not found: " + path);
                return;
            }

            string destination = args["destination"].ToString();
            string targetEntryName = args.ContainsKey("entry") && args["entry"] != null ? args["entry"].ToString() : null;

            try
            {
                using (var arc = ArcFile.TryOpen(path))
                {
                    if (arc == null)
                    {
                        WriteError(id, "UNSUPPORTED_FORMAT", "File format is not recognized as a supported archive: " + path);
                        return;
                    }

                    string fullDest = Path.GetFullPath(destination);
                    if (!Directory.Exists(fullDest))
                    {
                        Directory.CreateDirectory(fullDest);
                    }

                    var entriesToExtract = new List<Entry>();
                    if (!string.IsNullOrEmpty(targetEntryName))
                    {
                        var found = arc.Dir.FirstOrDefault(e => e.Name.Equals(targetEntryName, StringComparison.OrdinalIgnoreCase));
                        if (found == null)
                        {
                            WriteError(id, "ENTRY_NOT_FOUND", "Entry not found in archive: " + targetEntryName);
                            return;
                        }
                        entriesToExtract.Add(found);
                    }
                    else
                    {
                        entriesToExtract.AddRange(arc.Dir);
                    }

                    bool doConvert = args.ContainsKey("convert") && Convert.ToBoolean(args["convert"]);
                    string targetImgTag = args.ContainsKey("image_format") && args["image_format"] != null ? args["image_format"].ToString() : "PNG";
                    string targetAudTag = args.ContainsKey("audio_format") && args["audio_format"] != null ? args["audio_format"].ToString() : "WAV";

                    ImageFormat targetImgFormat = null;
                    AudioFormat targetAudFormat = null;
                    if (doConvert)
                    {
                        targetImgFormat = FormatCatalog.Instance.ImageFormats.FirstOrDefault(f => f.Tag.Equals(targetImgTag, StringComparison.OrdinalIgnoreCase))
                            ?? FormatCatalog.Instance.LookupExtension<ImageFormat>("png").FirstOrDefault();
                        targetAudFormat = FormatCatalog.Instance.AudioFormats.FirstOrDefault(f => f.Tag.Equals(targetAudTag, StringComparison.OrdinalIgnoreCase))
                            ?? FormatCatalog.Instance.LookupExtension<AudioFormat>("wav").FirstOrDefault();
                    }

                    var extractedEntries = new List<string>();
                    long totalBytes = 0;

                    foreach (var entry in entriesToExtract)
                    {
                        string normalizedEntryName = entry.Name.Replace('\\', '/').TrimStart('/');

                        if (doConvert && targetImgFormat != null && (entry.Type == "image" || HasImageExtension(entry.Name)))
                        {
                            try
                            {
                                using (var decoder = arc.OpenImage(entry))
                                {
                                    if (decoder != null)
                                    {
                                        var img = decoder.Image;
                                        string targetExt = targetImgFormat.Extensions.FirstOrDefault() ?? "png";
                                        string convertedName = Path.ChangeExtension(normalizedEntryName, targetExt);
                                        string targetPath = Path.Combine(fullDest, convertedName);
                                        string fullTargetPath = Path.GetFullPath(targetPath);

                                        if (!fullTargetPath.StartsWith(fullDest, StringComparison.OrdinalIgnoreCase))
                                        {
                                            WriteError(id, "UNSAFE_PATH", "Archive entry path escapes destination: " + entry.Name);
                                            return;
                                        }

                                        string targetDir = Path.GetDirectoryName(fullTargetPath);
                                        if (!string.IsNullOrEmpty(targetDir) && !Directory.Exists(targetDir))
                                            Directory.CreateDirectory(targetDir);

                                        using (var output = File.Create(fullTargetPath))
                                        {
                                            targetImgFormat.Write(output, img);
                                            totalBytes += output.Length;
                                        }
                                        extractedEntries.Add(convertedName);
                                        continue;
                                    }
                                }
                            }
                            catch
                            {
                                // Fall through to standard extraction
                            }
                        }

                        if (doConvert && targetAudFormat != null && (entry.Type == "audio" || HasAudioExtension(entry.Name)))
                        {
                            try
                            {
                                using (var entryStream = arc.OpenEntry(entry))
                                using (var binStream = new BinaryStream(entryStream, entry.Name))
                                using (var sound = AudioFormat.Read(binStream))
                                {
                                    if (sound != null)
                                    {
                                        string targetExt = targetAudFormat.Extensions.FirstOrDefault() ?? "wav";
                                        string convertedName = Path.ChangeExtension(normalizedEntryName, targetExt);
                                        string targetPath = Path.Combine(fullDest, convertedName);
                                        string fullTargetPath = Path.GetFullPath(targetPath);

                                        if (!fullTargetPath.StartsWith(fullDest, StringComparison.OrdinalIgnoreCase))
                                        {
                                            WriteError(id, "UNSAFE_PATH", "Archive entry path escapes destination: " + entry.Name);
                                            return;
                                        }

                                        string targetDir = Path.GetDirectoryName(fullTargetPath);
                                        if (!string.IsNullOrEmpty(targetDir) && !Directory.Exists(targetDir))
                                            Directory.CreateDirectory(targetDir);

                                        using (var output = File.Create(fullTargetPath))
                                        {
                                            targetAudFormat.Write(sound, output);
                                            totalBytes += output.Length;
                                        }
                                        extractedEntries.Add(convertedName);
                                        continue;
                                    }
                                }
                            }
                            catch
                            {
                                // Fall through to standard extraction
                            }
                        }

                        string standardTargetPath = Path.Combine(fullDest, normalizedEntryName);
                        string fullStandardPath = Path.GetFullPath(standardTargetPath);

                        if (!fullStandardPath.StartsWith(fullDest, StringComparison.OrdinalIgnoreCase))
                        {
                            WriteError(id, "UNSAFE_PATH", "Archive entry path escapes destination: " + entry.Name);
                            return;
                        }

                        string stdDir = Path.GetDirectoryName(fullStandardPath);
                        if (!string.IsNullOrEmpty(stdDir) && !Directory.Exists(stdDir))
                        {
                            Directory.CreateDirectory(stdDir);
                        }

                        using (var input = arc.OpenEntry(entry))
                        using (var output = File.Create(fullStandardPath))
                        {
                            input.CopyTo(output);
                            totalBytes += output.Length;
                        }
                        extractedEntries.Add(entry.Name);
                    }

                    WriteSuccess(id, new Dictionary<string, object>
                    {
                        { "extracted_count", extractedEntries.Count },
                        { "total_bytes", totalBytes },
                        { "destination", fullDest },
                        { "entries", extractedEntries }
                    });
                }
            }
            catch (UnknownEncryptionScheme ex)
            {
                WriteError(id, "ENCRYPTED_ARCHIVE", "Archive is encrypted: " + ex.Message);
            }
            catch (InvalidEncryptionScheme ex)
            {
                WriteError(id, "ENCRYPTED_ARCHIVE", "Invalid encryption scheme: " + ex.Message);
            }
            catch (Exception ex)
            {
                WriteError(id, "EXTRACT_FAILED", ex.Message);
            }
        }

        static void HandleConvertImage(string id, Dictionary<string, object> args)
        {
            if (!args.ContainsKey("path") || args["path"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'path'");
                return;
            }
            if (!args.ContainsKey("destination") || args["destination"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'destination'");
                return;
            }

            string path = args["path"].ToString();
            if (!File.Exists(path))
            {
                WriteError(id, "FILE_NOT_FOUND", "File not found: " + path);
                return;
            }

            string destination = args["destination"].ToString();
            string targetTag = args.ContainsKey("format") && args["format"] != null ? args["format"].ToString() : "PNG";

            ImageFormat targetFormat = FormatCatalog.Instance.ImageFormats.FirstOrDefault(f => f.Tag.Equals(targetTag, StringComparison.OrdinalIgnoreCase))
                ?? FormatCatalog.Instance.LookupExtension<ImageFormat>(targetTag.ToLowerInvariant()).FirstOrDefault()
                ?? FormatCatalog.Instance.LookupExtension<ImageFormat>("png").FirstOrDefault();

            if (targetFormat == null || !targetFormat.CanWrite)
            {
                WriteError(id, "UNSUPPORTED_OUTPUT_FORMAT", "Target image format cannot be written or unsupported: " + targetTag);
                return;
            }

            try
            {
                ImageData image;
                using (var file = BinaryStream.FromFile(path))
                {
                    image = ImageFormat.Read(file);
                    if (image == null)
                    {
                        WriteError(id, "UNSUPPORTED_FORMAT", "Image format not recognized: " + path);
                        return;
                    }
                }

                string fullDest = Path.GetFullPath(destination);
                string dir = Path.GetDirectoryName(fullDest);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                using (var outfile = File.Create(fullDest))
                {
                    targetFormat.Write(outfile, image);
                }

                WriteSuccess(id, new Dictionary<string, object>
                {
                    { "width", (int)image.Width },
                    { "height", (int)image.Height },
                    { "bpp", image.BPP },
                    { "target_format", targetFormat.Tag },
                    { "destination", fullDest }
                });
            }
            catch (Exception ex)
            {
                WriteError(id, "CONVERT_FAILED", ex.Message);
            }
        }

        static void HandleConvertAudio(string id, Dictionary<string, object> args)
        {
            if (!args.ContainsKey("path") || args["path"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'path'");
                return;
            }
            if (!args.ContainsKey("destination") || args["destination"] == null)
            {
                WriteError(id, "INVALID_ARGUMENTS", "Missing required argument 'destination'");
                return;
            }

            string path = args["path"].ToString();
            if (!File.Exists(path))
            {
                WriteError(id, "FILE_NOT_FOUND", "File not found: " + path);
                return;
            }

            string destination = args["destination"].ToString();
            string targetTag = args.ContainsKey("format") && args["format"] != null ? args["format"].ToString() : "WAV";

            AudioFormat targetFormat = FormatCatalog.Instance.AudioFormats.FirstOrDefault(f => f.Tag.Equals(targetTag, StringComparison.OrdinalIgnoreCase))
                ?? FormatCatalog.Instance.LookupExtension<AudioFormat>(targetTag.ToLowerInvariant()).FirstOrDefault()
                ?? FormatCatalog.Instance.LookupExtension<AudioFormat>("wav").FirstOrDefault();

            if (targetFormat == null || !targetFormat.CanWrite)
            {
                WriteError(id, "UNSUPPORTED_OUTPUT_FORMAT", "Target audio format cannot be written or unsupported: " + targetTag);
                return;
            }

            try
            {
                string fullDest = Path.GetFullPath(destination);
                string dir = Path.GetDirectoryName(fullDest);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                using (var file = BinaryStream.FromFile(path))
                using (var sound = AudioFormat.Read(file))
                {
                    if (sound == null)
                    {
                        WriteError(id, "UNSUPPORTED_FORMAT", "Audio format not recognized: " + path);
                        return;
                    }

                    using (var outfile = File.Create(fullDest))
                    {
                        targetFormat.Write(sound, outfile);
                    }

                    WriteSuccess(id, new Dictionary<string, object>
                    {
                        { "sample_rate", (int)sound.Format.SamplesPerSecond },
                        { "channels", (int)sound.Format.Channels },
                        { "bits_per_sample", (int)sound.Format.BitsPerSample },
                        { "target_format", targetFormat.Tag },
                        { "destination", fullDest }
                    });
                }
            }
            catch (Exception ex)
            {
                WriteError(id, "CONVERT_FAILED", ex.Message);
            }
        }

        static bool HasImageExtension(string name)
        {
            string ext = Path.GetExtension(name);
            if (string.IsNullOrEmpty(ext)) return false;
            ext = ext.TrimStart('.').ToLowerInvariant();
            return FormatCatalog.Instance.LookupExtension<ImageFormat>(ext).Any();
        }

        static bool HasAudioExtension(string name)
        {
            string ext = Path.GetExtension(name);
            if (string.IsNullOrEmpty(ext)) return false;
            ext = ext.TrimStart('.').ToLowerInvariant();
            return FormatCatalog.Instance.LookupExtension<AudioFormat>(ext).Any();
        }

        static void WriteSuccess(string id, object result)
        {
            var res = new Dictionary<string, object>
            {
                { "id", id },
                { "ok", true },
                { "result", result }
            };
            Console.WriteLine(m_serializer.Serialize(res));
            Console.Out.Flush();
        }

        static void WriteError(string id, string code, string message)
        {
            var res = new Dictionary<string, object>
            {
                { "id", id },
                { "ok", false },
                { "error", new Dictionary<string, object>
                    {
                        { "code", code },
                        { "message", message }
                    }
                }
            };
            Console.WriteLine(m_serializer.Serialize(res));
            Console.Out.Flush();
        }
    }
}
